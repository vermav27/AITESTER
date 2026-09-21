#!/usr/bin/env python3
"""Tool — fetch a Jira issue as raw JSON.

Contract (``llm.md`` §6): ``fetch_jira`` takes a KEY plus env config and writes
the raw issue JSON to stdout. Failures exit non-zero with the structured error
shape ``{"error": true, "http": ..., "message": ..., "key": ...}``.

Usage:  python tools/fetch_jira.py KAN-1
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import config_manager, jira_client  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a Jira issue as raw JSON.", epilog=ENV_EPILOG)
    parser.add_argument("key", help="Jira issue key, e.g. KAN-1")
    args = parser.parse_args()

    try:
        issue = jira_client.fetch_issue(args.key.upper(), config_manager.load_config())
    except jira_client.JiraError as exc:
        json.dump(exc.to_dict(), sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 1

    json.dump(issue, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
