"""Groq API client (OpenAI-compatible chat completions).

Used as the alternative AI provider. The API key is read from config and
never appears in logs, UI, or exception messages.
"""

from __future__ import annotations

from typing import Dict

import requests

TIMEOUT_SECONDS = 60
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqServiceError(Exception):
    """Raised when a Groq request fails. Message is always user-safe."""


def _api_key(config: Dict[str, str]) -> str:
    key = config.get("GROQ_API_KEY", "").strip()
    if not key:
        raise GroqServiceError("Groq API key is not configured.")
    return key


def _model(config: Dict[str, str]) -> str:
    return config.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()


def generate(prompt: str, config: Dict[str, str]) -> str:
    """Generate a chat completion for ``prompt`` via Groq."""
    headers = {
        "Authorization": f"Bearer {_api_key(config)}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _model(config),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise GroqServiceError("Unable to reach the Groq API. Check your network.")
    except requests.exceptions.Timeout:
        raise GroqServiceError("Groq request timed out. Try again.")
    except requests.exceptions.RequestException as exc:
        raise GroqServiceError(f"Groq request failed: {exc.__class__.__name__}")

    if response.status_code in (401, 403):
        raise GroqServiceError("Groq authentication failed. Check your API key.")
    if response.status_code == 404:
        raise GroqServiceError(
            f"Groq model '{_model(config)}' is not available. Check the model name."
        )
    if response.status_code == 429:
        raise GroqServiceError("Groq rate limit exceeded. Try again in a moment.")
    if response.status_code >= 400:
        raise GroqServiceError(f"Groq returned an error (HTTP {response.status_code}).")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError):
        raise GroqServiceError("Groq returned an unreadable response.")
    if not content:
        raise GroqServiceError("Groq returned an empty response.")
    return content


def test_connection(config: Dict[str, str]) -> None:
    """Verify the Groq API key works by listing available models.

    Raises GroqServiceError with a user-safe message on failure.
    """
    headers = {"Authorization": f"Bearer {_api_key(config)}"}
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models", headers=headers, timeout=15
        )
    except requests.exceptions.ConnectionError:
        raise GroqServiceError("Unable to reach the Groq API. Check your network.")
    except requests.exceptions.Timeout:
        raise GroqServiceError("Groq connection timed out.")
    except requests.exceptions.RequestException as exc:
        raise GroqServiceError(f"Groq request failed: {exc.__class__.__name__}")

    if response.status_code in (401, 403):
        raise GroqServiceError("Groq authentication failed. Check your API key.")
    if response.status_code >= 400:
        raise GroqServiceError(f"Groq returned an error (HTTP {response.status_code}).")
