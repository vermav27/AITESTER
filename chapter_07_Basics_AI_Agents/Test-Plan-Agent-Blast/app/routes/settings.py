"""Settings routes — save configuration and test the Jira / Ollama links.

Phase 2 (Link) of the B.L.A.S.T. protocol lives here: the connection tests are
the handshake that proves both external services respond before any planning
work is attempted.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from core import config_manager, jira_client, ollama_client

bp = Blueprint("settings", __name__, url_prefix="/settings")
log = logging.getLogger(__name__)

# Fields rendered on the page, grouped for the template.
JIRA_FIELDS = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_TOKEN", "JIRA_AC_FIELD_ID"]
OLLAMA_FIELDS = ["OLLAMA_BASE_URL", "OLLAMA_MODEL"]


def _form_config() -> Dict[str, str]:
    """Merge the saved config with any values currently typed in the form.

    This lets "Test connection" validate what the user sees on screen, without
    requiring a save first. A blank secret field keeps the stored secret.
    """
    config = config_manager.load_config()
    for key in config_manager.DEFAULT_CONFIG:
        submitted = request.form.get(key)
        if submitted is None:
            continue
        submitted = submitted.strip()
        if submitted:
            config[key] = submitted
    return config


@bp.get("/", strict_slashes=False)
def page():
    config = config_manager.load_config()
    return render_template(
        "settings.html",
        config=config,
        state=config_manager.connection_state(config),
        masked_token=config_manager.mask_secret(config.get("JIRA_TOKEN", "")),
        installed_models=ollama_client.list_models(config),
        jira_fields=JIRA_FIELDS,
        ollama_fields=OLLAMA_FIELDS,
    )


@bp.post("/")
def save():
    """Persist the submitted settings into the gitignored ``.env`` file."""
    updates = {
        key: (request.form.get(key) or "")
        for key in config_manager.DEFAULT_CONFIG
        if key in request.form
    }
    saved = config_manager.save_config(updates)
    changed = [key for key, value in updates.items() if value.strip()]
    log.info("Settings saved (non-secret fields updated: %s)", ", ".join(sorted(set(changed) - config_manager.SECRET_KEYS)))
    flash(f"Configuration saved to .env — {len(set(changed))} value(s) updated.", "success")
    if not config_manager.connection_state(saved)["jira_configured"]:
        flash("Jira still looks unconfigured. Base URL, Email and API token are all required.", "warning")
    return redirect(url_for("settings.page"))


def _result(ok: bool, message: str) -> Any:
    """Uniform JSON shape for both connection tests (always HTTP 200)."""
    return jsonify({"ok": ok, "message": message})


@bp.post("/test/jira")
def test_jira():
    """Handshake: prove the Jira credentials work (``GET /rest/api/3/myself``)."""
    config = _form_config()
    if not config.get("JIRA_BASE_URL"):
        return _result(False, "Enter a Jira Base URL first.")
    try:
        info = jira_client.test_connection(config)
    except jira_client.JiraError as exc:
        return _result(False, exc.message)
    return _result(True, info["message"])


@bp.post("/test/ollama")
def test_ollama():
    """Handshake: prove the local Ollama server answers and has the model."""
    config = _form_config()
    try:
        info = ollama_client.test_connection(config)
    except ollama_client.OllamaError as exc:
        return _result(False, str(exc))
    return _result(True, info["message"])
