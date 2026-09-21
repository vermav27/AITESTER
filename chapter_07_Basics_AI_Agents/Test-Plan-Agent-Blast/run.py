"""Entry point — ``python run.py`` starts the local Flask server."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

# Load .env so host/port overrides work; core.config_manager reads the file directly.
load_dotenv(PROJECT_ROOT / ".env", override=False)

from app import create_app  # noqa: E402  (import after env load)

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "127.0.0.1")
    port = int(os.environ.get("APP_PORT", "5000"))
    debug = os.environ.get("APP_DEBUG", "1") == "1"
    print(f"\n  Test Plan Agent running at http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)
