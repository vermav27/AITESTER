#!/usr/bin/env python3
"""Tool — fetch an issue's comments as JSON.

Acceptance criteria frequently live only in comments, so this is a separate
call rather than an assumed field on the issue payload.

Usage:  python tools/fetch_comments.py KAN-1
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import config_manager, jira_client  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Jira comments as JSON.", epilog=ENV_EPILOG)
    parser.add_argument("key", help="Jira issue key, e.g. KAN-1")
    args = parser.parse_args()

    try:
        comments = jira_client.fetch_comments(args.key.upper(), config_manager.load_config())
    except jira_client.JiraError as exc:
        json.dump(exc.to_dict(), sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 1

    json.dump({"comments": comments, "count": len(comments)}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
