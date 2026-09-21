#!/usr/bin/env python3
"""Tool — run the whole pipeline from the command line (L2 Navigation).

The same code path the web UI uses, without the browser. Useful for validating
the pipeline and for scripting.

Usage:  python tools/run_agent.py "create a test plan for KAN-1"
        python tools/run_agent.py "latest ticket in VWO" --markdown-only
"""

from __future__ import annotations

import argparse
import json
import sys

from _bootstrap import ENV_EPILOG  # noqa: E402

from core import navigation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full test plan pipeline.", epilog=ENV_EPILOG)
    parser.add_argument("prompt", help="natural-language request, e.g. 'create a test plan for KAN-1'")
    parser.add_argument("--json", action="store_true", help="emit the full result payload as JSON")
    parser.add_argument("--markdown-only", action="store_true", help="print only the rendered plan")
    args = parser.parse_args()

    def progress(message: str) -> None:
        if not args.json and not args.markdown_only:
            print(f"  … {message}", file=sys.stderr)

    try:
        result = navigation.run(args.prompt, progress=progress)
    except navigation.NavigationError as exc:
        print(f"\n✗ Stopped at '{exc.step}': {exc.message}\n", file=sys.stderr)
        return 1

    if args.json:
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    elif args.markdown_only:
        sys.stdout.write(result["plan_markdown"])
    else:
        for step in result["steps"]:
            print(f"  ✓ {step['name']}: {step['detail']}")
        print()
        print(f"  {result['key']} — {result['title']}")
        print(f"  {result['gap_count']} gap(s) · {result['scenario_count']} scenario(s) · {result['duration_seconds']}s")
        print(f"  {result['artifacts']['markdown_path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
