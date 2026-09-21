"""L3 tool — configuration manager.

The project ``.env`` file is the single source of truth for configuration
(invariant I4). This module loads it, writes edits back to it, and masks
secrets for safe display in the UI.

Design note: we deliberately do **not** call ``load_dotenv()``. That function
mutates ``os.environ``, which then shadows the freshly saved file on the next
read and makes the Settings page appear to "not save". Reading the file
directly keeps ``.env`` authoritative and never stale. Real OS environment
variables are used only to fill keys that are absent from the file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Set

from dotenv import dotenv_values, set_key

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Keys whose values must never be rendered in plain text.
SECRET_KEYS: Set[str] = {"JIRA_TOKEN"}

DEFAULT_CONFIG: Dict[str, str] = {
    "JIRA_BASE_URL": "",
    "JIRA_EMAIL": "",
    "JIRA_TOKEN": "",
    "JIRA_AC_FIELD_ID": "",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "gemma3:4b",
}


def load_config() -> Dict[str, str]:
    """Return the effective configuration as a plain dict.

    Values come from ``.env`` first; a real OS environment variable is used
    only when the file has no value for that key.
    """
    file_values = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
    config: Dict[str, str] = {}
    for key, default in DEFAULT_CONFIG.items():
        file_value = file_values.get(key)
        if file_value:
            config[key] = str(file_value).strip()
        else:
            env_value = os.environ.get(key, "").strip()
            config[key] = env_value or default
    return config


def save_config(updates: Dict[str, str]) -> Dict[str, str]:
    """Merge non-empty ``updates`` into ``.env`` and return the new config.

    Blank values are skipped so that an empty password-style input keeps the
    stored secret instead of erasing it.
    """
    ENV_FILE.touch(exist_ok=True)
    for key, value in updates.items():
        if key not in DEFAULT_CONFIG:
            continue
        value = (value or "").strip()
        if value:
            set_key(str(ENV_FILE), key, value)
    return load_config()


def mask_secret(value: str, visible: int = 4) -> str:
    """Return a masked representation of a secret for display, e.g. ``ATATT3…4BE68``."""
    if not value:
        return ""
    if len(value) <= visible + 6:
        return "•" * 8
    return f"{value[:6]}…{value[-visible:]}"


def connection_state(config: Dict[str, str]) -> Dict[str, bool]:
    """Report which external services have enough configuration to be tried."""
    return {
        "jira_configured": bool(
            config.get("JIRA_BASE_URL")
            and config.get("JIRA_EMAIL")
            and config.get("JIRA_TOKEN")
        ),
        "ollama_configured": bool(config.get("OLLAMA_BASE_URL")),
    }
