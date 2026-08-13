"""LLM provider dispatch.

Keeps test-generation logic independent of any single AI provider. Chooses the
provider from config (``AI_PROVIDER``) and optionally falls back from Ollama to
Groq when Ollama is unreachable and a Groq key is configured.
"""

from __future__ import annotations

from typing import Dict

from . import groq_service, ollama_service


class LLMServiceError(Exception):
    """Raised when every configured provider fails. Message is user-safe."""


def generate_response(prompt: str, config: Dict[str, str]) -> tuple[str, str]:
    """Generate a response for ``prompt`` and return ``(content, provider_used)``.

    Provider selection:
        - ``AI_PROVIDER=groq``  → Groq only (no fallback).
        - ``AI_PROVIDER=ollama`` (default) → Ollama; on failure, fall back to
          Groq if a Groq API key is configured.

    Raises:
        LLMServiceError: When no provider could generate a response.
    """
    provider = config.get("AI_PROVIDER", "ollama").strip().lower()
    errors: list[str] = []

    if provider == "groq":
        try:
            return groq_service.generate(prompt, config), "groq"
        except groq_service.GroqServiceError as exc:
            raise LLMServiceError(f"Groq: {exc}")

    # Default path: Ollama with optional Groq fallback.
    try:
        return ollama_service.generate(prompt, config), "ollama"
    except ollama_service.OllamaServiceError as exc:
        errors.append(f"Ollama: {exc}")

    if config.get("GROQ_API_KEY", "").strip():
        try:
            return groq_service.generate(prompt, config), "groq (fallback)"
        except groq_service.GroqServiceError as exc:
            errors.append(f"Groq fallback: {exc}")

    raise LLMServiceError(" | ".join(errors) or "No AI provider is configured.")
