"""Ollama API client for the local LLM.

Talks only to the local Ollama server (default http://localhost:11434) using
its native ``/api/generate`` and ``/api/tags`` endpoints. The model name is
read from config so it works with whatever Gemma 3 tag is installed locally.
"""

from __future__ import annotations

from typing import Dict

import requests

TIMEOUT_SECONDS = 120  # local model generation can be slow on CPU


class OllamaServiceError(Exception):
    """Raised when an Ollama request fails. Message is always user-safe."""


def _base_url(config: Dict[str, str]) -> str:
    return config.get("OLLAMA_BASE_URL", "http://localhost:11434").strip().rstrip("/")


def _model(config: Dict[str, str]) -> str:
    model = config.get("OLLAMA_MODEL", "gemma3:1b").strip()
    if not model:
        raise OllamaServiceError("Ollama model name is not configured.")
    return model


def generate(prompt: str, config: Dict[str, str]) -> str:
    """Generate a completion for ``prompt`` using the configured model."""
    base = _base_url(config)
    url = f"{base}/api/generate"
    payload = {"model": _model(config), "prompt": prompt, "stream": False}

    try:
        response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise OllamaServiceError(
            f"Unable to reach Ollama at {base}. Is it running? (try: ollama serve)"
        )
    except requests.exceptions.Timeout:
        raise OllamaServiceError("Ollama request timed out. The model may be loading or busy.")
    except requests.exceptions.RequestException as exc:
        raise OllamaServiceError(f"Ollama request failed: {exc.__class__.__name__}")

    if response.status_code == 404:
        raise OllamaServiceError(
            f"Ollama model '{_model(config)}' is not installed. "
            "Run 'ollama list' to see available models."
        )
    if response.status_code >= 400:
        raise OllamaServiceError(f"Ollama returned an error (HTTP {response.status_code}).")

    try:
        data = response.json()
    except ValueError:
        raise OllamaServiceError("Ollama returned an unreadable response.")

    content = (data.get("response") or "").strip()
    if not content:
        raise OllamaServiceError("Ollama returned an empty response.")
    return content


def list_models(config: Dict[str, str]) -> list[str]:
    """Return the names of locally installed Ollama models."""
    base = _base_url(config)
    try:
        response = requests.get(f"{base}/api/tags", timeout=10)
        response.raise_for_status()
        return [m.get("name", "") for m in response.json().get("models", [])]
    except requests.exceptions.RequestException:
        return []


def test_connection(config: Dict[str, str]) -> None:
    """Verify the local Ollama server responds and the model exists.

    Raises OllamaServiceError with a user-safe message on failure.
    """
    base = _base_url(config)
    try:
        response = requests.get(f"{base}/api/tags", timeout=10)
    except requests.exceptions.ConnectionError:
        raise OllamaServiceError(
            f"Unable to reach Ollama at {base}. Is it running? (try: ollama serve)"
        )
    except requests.exceptions.Timeout:
        raise OllamaServiceError("Ollama connection timed out.")
    except requests.exceptions.RequestException as exc:
        raise OllamaServiceError(f"Ollama request failed: {exc.__class__.__name__}")

    if response.status_code >= 400:
        raise OllamaServiceError(f"Ollama returned an error (HTTP {response.status_code}).")

    installed = {m.get("name", "") for m in response.json().get("models", [])}
    model = _model(config)
    if model not in installed:
        raise OllamaServiceError(
            f"Ollama is running, but model '{model}' is not installed. "
            f"Installed models: {', '.join(sorted(installed)) or 'none'}."
        )
