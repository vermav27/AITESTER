#!/usr/bin/env python3
"""Tool — Link handshake (B.L.A.S.T. Phase 2).

Proves both external services respond before any planning work is attempted:
Jira credentials via ``GET /rest/api/3/myself`` and the local Ollama server via
``GET /api/tags``.

Usage:  python tools/verify_connections.py
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import config_manager, jira_client, ollama_client  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the Jira and Ollama connections.", epilog=ENV_EPILOG)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    config = config_manager.load_config()
    reports: list = []
    ok = True

    try:
        info = jira_client.test_connection(config)
        reports.append({"service": "jira", "ok": True, "message": info["message"]})
    except jira_client.JiraError as exc:
        ok = False
        reports.append({"service": "jira", "ok": False, "message": exc.message})

    try:
        info = ollama_client.test_connection(config)
        reports.append({"service": "ollama", "ok": True, "message": info["message"]})
    except ollama_client.OllamaError as exc:
        ok = False
        reports.append({"service": "ollama", "ok": False, "message": str(exc)})

    if args.json:
        json.dump({"ok": ok, "services": reports}, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        for report in reports:
            print(f"  {'✓' if report['ok'] else '✗'} {report['service']:<7} {report['message']}")
        print()
        print("Link verified — both services are reachable." if ok else "Link broken — fix the failures above.")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
