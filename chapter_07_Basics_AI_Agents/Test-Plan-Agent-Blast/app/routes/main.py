"""Generate page routes — the prompt UI and run artifact downloads."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import (
    Blueprint,
    flash,
    render_template,
    request,
    send_from_directory,
)

from core import config_manager, navigation
from core.render import RUNS_DIR

bp = Blueprint("main", __name__)
log = logging.getLogger(__name__)

MAX_RECENT_RUNS = 6

EXAMPLES = [
    "Fetch this Jira and create a test plan for KAN-1",
    "Create a test plan for the latest ticket in KAN",
    "Write a test plan for ticket KAN-5",
]


def recent_runs() -> List[Dict[str, Any]]:
    """List the most recently generated plans from ``runs/``."""
    if not RUNS_DIR.exists():
        return []
    files = sorted(RUNS_DIR.glob("*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
    runs: List[Dict[str, Any]] = []
    for path in files[:MAX_RECENT_RUNS]:
        stat = path.stat()
        runs.append(
            {
                "name": path.name,
                "key": path.name.split("-test-plan-")[0],
                "size_kb": round(stat.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d %b, %H:%M"),
            }
        )
    return runs


def page_context(**extra: Any) -> Dict[str, Any]:
    """Everything the index template needs, including live config state."""
    config = config_manager.load_config()
    context: Dict[str, Any] = {
        "config": config,
        "state": config_manager.connection_state(config),
        "masked_token": config_manager.mask_secret(config.get("JIRA_TOKEN", "")),
        "recent_runs": recent_runs(),
        "examples": EXAMPLES,
        "result": None,
        "prompt": "",
        "error": None,
        "steps": [],
    }
    context.update(extra)
    return context


@bp.get("/")
def index():
    return render_template("index.html", **page_context())


@bp.post("/generate")
def generate():
    """Run the full pipeline for the submitted prompt and render the result."""
    prompt = (request.form.get("prompt") or "").strip()
    if not prompt:
        flash("Enter a request first — for example: create a test plan for KAN-1.", "warning")
        return render_template("index.html", **page_context()), 400

    state = config_manager.connection_state(config_manager.load_config())
    if not state["jira_configured"] or not state["ollama_configured"]:
        flash("Configure Jira and Ollama on the Settings page before generating.", "warning")
        return render_template("index.html", **page_context(prompt=prompt)), 400

    try:
        result = navigation.run(prompt)
    except navigation.NavigationError as exc:
        log.warning("Generation stopped at '%s': %s", exc.step, exc.message)
        return (
            render_template(
                "index.html",
                **page_context(prompt=prompt, error=exc.message, failed_step=exc.step, steps=exc.steps),
            ),
            400,
        )
    except Exception as exc:  # noqa: BLE001 — surface the class name, never the traceback
        log.exception("Unexpected failure while generating a plan")
        return (
            render_template(
                "index.html",
                **page_context(
                    prompt=prompt,
                    error=f"Unexpected error ({exc.__class__.__name__}). Check the server log for details.",
                ),
            ),
            500,
        )

    return render_template("index.html", **page_context(result=result, prompt=prompt))


@bp.get("/runs/<path:filename>")
def download_run(filename: str):
    """Download a generated artifact (Markdown or JSON) from ``runs/``."""
    if Path(filename).suffix not in (".md", ".json"):
        return "Not found", 404
    return send_from_directory(RUNS_DIR, filename, as_attachment=True)
