"""Allow the standalone tools to import the shared ``core`` package."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Common argparse epilog so every tool documents the same environment inputs.
ENV_EPILOG = (
    "configuration: read from the project .env (JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN, "
    "OLLAMA_BASE_URL, OLLAMA_MODEL). Secrets are never printed."
)
