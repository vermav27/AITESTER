#!/usr/bin/env python3
"""Tool — render a ``TestPlanDocument`` into the final Markdown artifact.

Two modes:

* ``--key`` + ``--draft``: fetch the ticket, compute gaps, take a draft body
  from a file, and render the standardized document.
* ``--document`` (or stdin): render an already-assembled TestPlanDocument JSON.

The rendered Markdown and JSON are written into ``runs/``.

Usage:  python tools/render_plan.py --key KAN-1 --draft draft.md
        python tools/render_plan.py --document plan.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import checklist, config_manager, jira_client, normalize, render  # noqa: E402


def _document_from_key(key: str, draft_path: Path) -> dict:
    config = config_manager.load_config()
    issue = jira_client.fetch_issue(key, config)
    comments = jira_client.fetch_comments(key, config)
    ticket = normalize.normalize_issue(issue, config, comments)
    gaps = checklist.analyze_gaps(ticket)
    draft_body = draft_path.read_text(encoding="utf-8")
    return render.build_document(ticket, gaps, draft_body, model="manual-draft")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a test plan document to Markdown.", epilog=ENV_EPILOG)
    parser.add_argument("--key", help="Jira issue key — requires --draft")
    parser.add_argument("--draft", help="path to a Markdown file holding the plan body")
    parser.add_argument("--document", help="path to an assembled TestPlanDocument JSON file")
    parser.add_argument("--from-stdin", action="store_true", help="read the TestPlanDocument JSON from stdin")
    args = parser.parse_args()

    try:
        if args.document or args.from_stdin:
            text = sys.stdin.read() if args.from_stdin else Path(args.document).read_text(encoding="utf-8")
            document = json.loads(text)
        elif args.key and args.draft:
            document = _document_from_key(args.key.upper(), Path(args.draft))
        else:
            parser.error("use --key with --draft, or --document / --from-stdin")
    except (jira_client.JiraError, OSError, json.JSONDecodeError) as exc:
        payload = exc.to_dict() if isinstance(exc, jira_client.JiraError) else {"error": True, "message": str(exc)}
        json.dump(payload, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 1

    markdown, artifacts = render.render_and_write(document)
    summary = {
        "key": document.get("jira_key"),
        "status": document.get("status"),
        "gaps": len(document.get("gaps") or []),
        "markdown": artifacts["markdown_path"],
        "json": artifacts["json_path"],
        "characters": len(markdown),
    }
    json.dump(summary, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
