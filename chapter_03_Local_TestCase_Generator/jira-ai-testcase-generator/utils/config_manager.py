"""Configuration manager.

Loads application settings from the local ``.env`` file (the single source of
truth) and saves edits made on the Settings page back to it. Secrets are never
printed; ``mask_secret`` is provided for safe display in the UI.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from dotenv import dotenv_values, load_dotenv, set_key

# Path to this project's root directory (one level above ``utils/``).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Non-secret keys are shown in plain text on the Settings page.
SECRET_KEYS = {"JIRA_API_TOKEN", "GROQ_API_KEY"}

DEFAULT_CONFIG: Dict[str, str] = {
    "JIRA_BASE_URL": "",
    "JIRA_EMAIL": "",
    "JIRA_API_TOKEN": "",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "gemma3:4b",
    "GROQ_API_KEY": "",
    "GROQ_MODEL": "llama-3.3-70b-versatile",
    "AI_PROVIDER": "ollama",
    "ACCEPTANCE_CRITERIA_FIELD_ID": "",
}


def load_config() -> Dict[str, str]:
    """Load configuration from the project ``.env`` file into a dict.

    Missing keys fall back to the defaults above. Any real environment
    variables with the same names take precedence, which lets power users
    override the file without editing it.
    """
    load_dotenv(ENV_FILE, override=False)
    file_values = dotenv_values(ENV_FILE)
    config = dict(DEFAULT_CONFIG)
    for key in config:
        env_value = os.environ.get(key)
        if env_value is not None:
            config[key] = env_value
        elif file_values.get(key):
            config[key] = file_values[key]
    return config


def save_config(updates: Dict[str, str]) -> Dict[str, str]:
    """Merge ``updates`` into the ``.env`` file.

    Only non-empty values are written so that blank Settings-page inputs do not
    erase existing secrets. Returns the resulting config.
    """
    for key, value in updates.items():
        if value and key in DEFAULT_CONFIG:
            set_key(str(ENV_FILE), key, value.strip())
    return load_config()


def mask_secret(value: str, visible: int = 4) -> str:
    """Return a masked representation of a secret for UI display.

    Example: ``sk-abc...1234``. Empty values return an empty string so the UI
    can show "Not configured".
    """
    if not value:
        return ""
    if len(value) <= visible + 6:
        return "••••"
    return f"{value[:6]}...{value[-visible:]}"
