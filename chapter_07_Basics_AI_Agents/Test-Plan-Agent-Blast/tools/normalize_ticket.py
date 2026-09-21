#!/usr/bin/env python3
"""Tool — normalize a Jira issue into ``TicketContext`` JSON.

Fetches the issue and its comments, flattens Atlassian Document Format, locates
acceptance criteria and records where each one came from.

Usage:  python tools/normalize_ticket.py KAN-1
        cat issue.json | python tools/normalize_ticket.py --from-stdin
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import config_manager, jira_client, normalize  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a Jira issue into TicketContext JSON.", epilog=ENV_EPILOG)
    parser.add_argument("key", nargs="?", help="Jira issue key, e.g. KAN-1")
    parser.add_argument("--from-stdin", action="store_true", help="read a raw issue JSON payload from stdin")
    args = parser.parse_args()

    config = config_manager.load_config()

    try:
        if args.from_stdin:
            raw_issue = json.load(sys.stdin)
            comments = ((raw_issue.get("fields") or {}).get("comment") or {}).get("comments") or []
        else:
            if not args.key:
                parser.error("provide an issue KEY or use --from-stdin")
            raw_issue = jira_client.fetch_issue(args.key.upper(), config)
            comments = jira_client.fetch_comments(args.key.upper(), config)
    except (jira_client.JiraError, json.JSONDecodeError) as exc:
        payload = exc.to_dict() if isinstance(exc, jira_client.JiraError) else {"error": True, "message": str(exc)}
        json.dump(payload, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 1

    ticket = normalize.normalize_issue(raw_issue, config, comments)
    json.dump(ticket, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
