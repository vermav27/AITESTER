#!/usr/bin/env python3
"""Tool — deterministic requirement gap analysis.

Runs the ticket through the requirement checklist and emits ``GapItem[]`` JSON.
Needs no LLM, so it is the fastest way to check what a ticket is missing.

Usage:  python tools/analyze_gaps.py KAN-1
        python tools/normalize_ticket.py KAN-1 | python tools/analyze_gaps.py --from-stdin
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import checklist, config_manager, jira_client, normalize  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze requirement gaps in a Jira ticket.", epilog=ENV_EPILOG
    )
    parser.add_argument("key", nargs="?", help="Jira issue key, e.g. KAN-1")
    parser.add_argument(
        "--from-stdin", action="store_true", help="read a TicketContext JSON payload from stdin"
    )
    args = parser.parse_args()

    config = config_manager.load_config()

    try:
        if args.from_stdin:
            ticket = json.load(sys.stdin)
        else:
            if not args.key:
                parser.error("provide an issue KEY or use --from-stdin")
            key = args.key.upper()
            issue = jira_client.fetch_issue(key, config)
            comments = jira_client.fetch_comments(key, config)
            ticket = normalize.normalize_issue(issue, config, comments)
    except (jira_client.JiraError, json.JSONDecodeError) as exc:
        payload = exc.to_dict() if isinstance(exc, jira_client.JiraError) else {"error": True, "message": str(exc)}
        json.dump(payload, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 1

    gaps = checklist.analyze_gaps(ticket)
    json.dump({"key": ticket.get("key"), "summary": checklist.summarize_gaps(gaps), "gaps": gaps}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
