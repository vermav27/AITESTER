"""Flask application factory for the Test Plan Agent.

Presentation layer only: routes render HTML and delegate every real action to
``core.navigation`` (L2), which in turn calls the L3 tools and the L1 agent.
"""

from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import Any, Dict

import markdown as markdown_lib
from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECRET_FILE = PROJECT_ROOT / ".flask_secret"

MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "attr_list"]

# Ticket descriptions and model output are untrusted input. Markdown passes raw
# HTML through untouched, so neutralise tags before conversion and drop script
# URLs afterwards. Autolinks such as <https://…> are preserved.
_HTML_TAG = re.compile(r"<(?=[a-zA-Z/!?])")
_AUTOLINK = re.compile(r"<([a-zA-Z][a-zA-Z0-9+.\-]*://[^>\s]+)>")
_UNSAFE_URL = re.compile(r'(href|src)\s*=\s*"(?:javascript|data|vbscript):[^"]*"', re.IGNORECASE)


def _neutralize_raw_html(text: str) -> str:
    """Escape HTML tags in untrusted text while keeping Markdown autolinks."""
    stashed: Dict[str, str] = {}

    def stash(match: re.Match) -> str:
        token = f"\x00{len(stashed)}\x00"
        stashed[token] = f"<{match.group(1)}>"
        return token

    text = _AUTOLINK.sub(stash, text)
    text = _HTML_TAG.sub("&lt;", text)
    for token, original in stashed.items():
        text = text.replace(token, original)
    return text


def _secret_key() -> str:
    """Return a stable dev secret so flash messages survive reloads.

    The value lives in a gitignored file; this app is local-only by design.
    """
    if SECRET_FILE.exists():
        stored = SECRET_FILE.read_text(encoding="utf-8").strip()
        if stored:
            return stored
    key = secrets.token_hex(32)
    SECRET_FILE.write_text(key, encoding="utf-8")
    return key


def render_markdown(text: str) -> str:
    """Convert the generated Markdown into HTML for the result panel."""
    if not text:
        return ""
    html = markdown_lib.markdown(_neutralize_raw_html(text), extensions=MARKDOWN_EXTENSIONS)
    return _UNSAFE_URL.sub(r'\1="#"', html)


def create_app() -> Flask:
    """Build the Flask app: config, blueprints, and template filters."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=_secret_key(),
        JSON_SORT_KEYS=False,
        TEMPLATES_AUTO_RELOAD=True,
    )

    from .routes.main import bp as main_bp
    from .routes.settings import bp as settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(settings_bp)

    app.jinja_env.filters["markdown"] = render_markdown
    app.jinja_env.globals["app_version"] = "1.0.0"

    return app
