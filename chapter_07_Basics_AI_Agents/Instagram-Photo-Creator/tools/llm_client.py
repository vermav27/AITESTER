"""Gemini adapter (Layer 3). One thin client used by `generate_backgrounds` and the
Settings 'Test connection' action. No other tool talks HTTP directly.
"""
from __future__ import annotations

import base64
import time

import requests

from config import load_settings


class LLMError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, kind: str = "LLMError"):
        super().__init__(message)
        self.message = message
        self.status = status
        self.kind = kind


def _llm_conf(override: dict | None = None) -> dict:
    conf = dict(load_settings()["llm"])
    for key, value in (override or {}).items():
        if value:
            conf[key] = value
    return conf


def _post(model: str, body: dict, timeout: int | None = None,
          conf_override: dict | None = None) -> dict:
    conf = _llm_conf(conf_override)
    key = conf.get("api_key") or ""
    if not key:
        raise LLMError("No API key configured. Add one in Settings.", kind="NoKey")
    url = f"{conf['base_url'].rstrip('/')}/models/{model}:generateContent"
    try:
        resp = requests.post(
            url,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json=body,
            timeout=timeout or conf.get("timeout", 120),
        )
    except requests.RequestException as exc:
        raise LLMError(f"Network error contacting {model}: {exc}", kind="Network") from exc

    if resp.status_code == 429:
        raise LLMError(
            f"Quota exceeded for {model} (HTTP 429). The key has no available quota for this model.",
            status=429, kind="QuotaExceeded",
        )
    if resp.status_code == 404:
        raise LLMError(f"Model not found: {model} (HTTP 404).", status=404, kind="ModelNotFound")
    if resp.status_code == 401 or resp.status_code == 403:
        raise LLMError(f"Authentication failed (HTTP {resp.status_code}). Check the API key.",
                       status=resp.status_code, kind="AuthFailed")
    if not resp.ok:
        snippet = resp.text[:300]
        raise LLMError(f"HTTP {resp.status_code} from {model}: {snippet}",
                       status=resp.status_code, kind="HttpError")

    try:
        return resp.json()
    except ValueError as exc:
        raise LLMError(f"Non-JSON response from {model}", kind="BadResponse") from exc


def test_connection(override: dict | None = None) -> dict:
    """Live check against the configured TEXT model. Returns a JSON-safe dict.

    `override` lets the Settings screen test an unsaved key WITHOUT persisting it.
    """
    conf = _llm_conf(override)
    model = conf.get("text_model", "")
    started = time.time()
    try:
        data = _post(model, {
            "contents": [{"parts": [{"text": "Reply with exactly: CONNECTION_OK"}]}]
        }, timeout=30, conf_override=override)
        latency = int((time.time() - started) * 1000)
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = " ".join(p.get("text", "") for p in parts).strip()
        return {
            "ok": True, "model": model, "latency_ms": latency,
            "reply": text[:120] or "(empty)", "provider": conf.get("provider"),
        }
    except LLMError as exc:
        return {
            "ok": False, "model": model, "kind": exc.kind,
            "error": exc.message, "status": exc.status,
            "latency_ms": int((time.time() - started) * 1000),
        }


def describe_image_model() -> dict:
    """Cheap probe: does the configured IMAGE model have quota? (text+image request, no image needed)."""
    conf = _llm_conf()
    model = conf.get("image_model", "")
    try:
        _post(model, {
            "contents": [{"parts": [{"text": "test"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }, timeout=30)
        return {"ok": True, "model": model}
    except LLMError as exc:
        return {"ok": False, "model": model, "kind": exc.kind, "error": exc.message}


def generate_image(prompt: str, aspect_ratio: str = "9:16",
                   timeout: int = 120) -> bytes:
    """Text-to-image via the configured IMAGE model. Returns PNG/JPEG bytes."""
    conf = _llm_conf()
    model = conf.get("image_model", "")
    data = _post(model, {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }, timeout=timeout)
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    raise LLMError("Model returned no image data.", kind="NoImage")
