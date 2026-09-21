"""L3 tool — Ollama client for the local LLM.

Transport only: it talks to the local Ollama server and returns text. It holds
no business judgement — prompt assembly lives in ``agent`` (the L1 layer), so
the deterministic/LLM boundary stays clean (invariant I1).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

TAGS_TIMEOUT_SECONDS = 10
GENERATE_TIMEOUT_SECONDS = 300  # a 4B model writing a full plan on CPU is slow

# Conservative defaults so a local model stays inside a sane context window.
DEFAULT_OPTIONS: Dict[str, Any] = {
    "temperature": 0.2,
    "num_ctx": 8192,
    "num_predict": 2048,
    "top_p": 0.9,
}


class OllamaError(Exception):
    """An Ollama call failed. ``message`` is always safe to show to the user."""


def _base_url(config: Dict[str, str]) -> str:
    return (config.get("OLLAMA_BASE_URL") or "http://localhost:11434").strip().rstrip("/")


def _model(config: Dict[str, str]) -> str:
    model = (config.get("OLLAMA_MODEL") or "").strip()
    if not model:
        raise OllamaError("Ollama model name is not configured. Set it on the Settings page.")
    return model


def list_models(config: Dict[str, str]) -> List[str]:
    """Return installed model tags. Returns an empty list if unreachable."""
    try:
        response = requests.get(f"{_base_url(config)}/api/tags", timeout=TAGS_TIMEOUT_SECONDS)
        response.raise_for_status()
        return sorted(
            model.get("name", "") for model in response.json().get("models", []) if model.get("name")
        )
    except (requests.exceptions.RequestException, ValueError):
        return []


def _connection_error(base: str) -> OllamaError:
    return OllamaError(f"Unable to reach Ollama at {base}. Is it running? (try: ollama serve)")


def chat(
    messages: List[Dict[str, str]],
    config: Dict[str, str],
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """Send a chat completion request and return the assistant's text."""
    base = _base_url(config)
    payload = {
        "model": _model(config),
        "messages": messages,
        "stream": False,
        "options": {**DEFAULT_OPTIONS, **(options or {})},
    }

    try:
        response = requests.post(
            f"{base}/api/chat", json=payload, timeout=GENERATE_TIMEOUT_SECONDS
        )
    except requests.exceptions.ConnectionError:
        raise _connection_error(base)
    except requests.exceptions.Timeout:
        raise OllamaError(
            "Ollama timed out while drafting the plan. A local 4B model can be slow — "
            "try a smaller ticket or a smaller model."
        )
    except requests.exceptions.RequestException as exc:
        raise OllamaError(f"Ollama request failed: {exc.__class__.__name__}.")

    if response.status_code == 404:
        raise OllamaError(
            f"Ollama model '{_model(config)}' is not installed. Run 'ollama list' to see available models."
        )
    if response.status_code >= 400:
        detail = ""
        try:
            detail = (response.json() or {}).get("error", "")
        except ValueError:
            detail = ""
        raise OllamaError(f"Ollama returned an error (HTTP {response.status_code}){': ' + detail if detail else ''}.")

    try:
        content = ((response.json() or {}).get("message") or {}).get("content", "")
    except ValueError:
        raise OllamaError("Ollama returned an unreadable response.")

    content = (content or "").strip()
    if not content:
        raise OllamaError("Ollama returned an empty response.")
    return content


def test_connection(config: Dict[str, str]) -> Dict[str, str]:
    """Verify the server responds and the configured model is installed."""
    base = _base_url(config)
    try:
        response = requests.get(f"{base}/api/tags", timeout=TAGS_TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise _connection_error(base)
    except requests.exceptions.Timeout:
        raise OllamaError("Ollama connection timed out.")
    except requests.exceptions.RequestException as exc:
        raise OllamaError(f"Ollama request failed: {exc.__class__.__name__}.")

    if response.status_code >= 400:
        raise OllamaError(f"Ollama returned an error (HTTP {response.status_code}).")

    try:
        installed = {
            model.get("name", "") for model in response.json().get("models", []) if model.get("name")
        }
    except ValueError:
        raise OllamaError("Ollama returned an unreadable model list.")

    model = _model(config)
    if model not in installed:
        available = ", ".join(sorted(installed)) or "none"
        raise OllamaError(
            f"Ollama is running, but model '{model}' is not installed. Installed models: {available}."
        )
    return {"model": model, "message": f"Ollama is running with model '{model}'."}
