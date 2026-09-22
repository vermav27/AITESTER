"""Central configuration: .env defaults overlaid with editable settings.json.

Layer 0/2 shared helper. Never logs or returns the raw API key.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"
TMP_DIR = BASE_DIR / ".tmp"
OUTPUT_DIR = BASE_DIR / "output"

load_dotenv(BASE_DIR / ".env")

_lock = threading.RLock()


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


DEFAULTS = {
    "llm": {
        "provider": "gemini",
        "api_key": _env("GEMINI_API_KEY"),
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "text_model": _env("GEMINI_TEXT_MODEL", "gemini-3.6-flash"),
        "image_model": _env("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image"),
        "timeout": 120,
    },
    "background_provider": _env("BACKGROUND_PROVIDER", "auto"),  # auto | gemini | local
    "brand": {
        "handle": _env("BRAND_HANDLE", "@meraki.by.ankita"),
        "opacity": 0.55,
        "size_pct": 0.15,
        "position": "bottom-right",
    },
    "canvas": {"width": 2160, "height": 3840},
}


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings() -> dict:
    with _lock:
        data = {}
        if SETTINGS_PATH.exists():
            try:
                data = json.loads(SETTINGS_PATH.read_text())
            except (json.JSONDecodeError, OSError):
                data = {}
        merged = _deep_merge(DEFAULTS, data)
        # An empty saved key must not clobber the .env key.
        if not merged["llm"].get("api_key"):
            merged["llm"]["api_key"] = _env("GEMINI_API_KEY")
        return merged


def save_settings(patch: dict) -> dict:
    with _lock:
        current = {}
        if SETTINGS_PATH.exists():
            try:
                current = json.loads(SETTINGS_PATH.read_text())
            except (json.JSONDecodeError, OSError):
                current = {}
        # never persist an empty api_key patch (means "leave unchanged")
        llm_patch = patch.get("llm")
        if isinstance(llm_patch, dict) and not llm_patch.get("api_key"):
            llm_patch.pop("api_key", None)
        merged = _deep_merge(current, patch)
        SETTINGS_PATH.write_text(json.dumps(merged, indent=2))
        return load_settings()


def mask_key(key: str) -> str:
    """Return a safe display form of an API key."""
    if not key:
        return ""
    if len(key) <= 10:
        return "•" * len(key)
    return f"{key[:4]}…{key[-4:]}"


def settings_for_browser() -> dict:
    """Settings payload safe to send to the browser (key masked)."""
    s = load_settings()
    view = json.loads(json.dumps(s))
    key = s["llm"].get("api_key", "")
    view["llm"]["api_key"] = mask_key(key)
    view["llm"]["has_key"] = bool(key)
    return view


def ensure_dirs() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
