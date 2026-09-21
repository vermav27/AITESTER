"""L3 tool — normalize a raw Jira issue into ``TicketContext``.

Interface frozen by ``llm.md`` §3.1. Two jobs:

1. Flatten Atlassian Document Format (ADF) into readable Markdown-ish text,
   preserving lists and tables so acceptance criteria survive flattening.
2. Locate acceptance criteria and record **where each one came from**
   (custom field → description → comment). If none exist the list stays empty —
   acceptance criteria are never inferred (rule R1 / R11).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Headings that introduce an acceptance-criteria block.
_AC_HEADING = re.compile(
    r"^\s*#{0,6}\s*(?:acceptance\s+criteria|acceptance\s+test[s]?|acceptance\s+condition[s]?"
    r"|done\s+when|definition\s+of\s+done|ac)\s*[:\-–]?\s*$",
    re.IGNORECASE,
)

# A different section heading ends the AC block.
_OTHER_HEADING = re.compile(
    r"^\s*#{1,6}\s+\S"
    r"|^\s*(?:description|steps?\s+to\s+reproduce|notes?|context|background|scope|out\s+of\s+scope"
    r"|test\s+data|dependencies|design|attachments?|references?|impact)\s*[:\-–]\s*$",
    re.IGNORECASE,
)

_TABLE_SEPARATOR = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
_LIST_PREFIX = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+")
_MARKER_KEYS = ("type", "text", "url")

# Rows that are table headers rather than criteria.
_AC_HEADER_CELLS = re.compile(
    r"^(?:#|no\.?|id|s\.?no\.?|acceptance\s+criteria|criteria|description|requirement)$",
    re.IGNORECASE,
)


def _apply_marks(text: str, marks: Optional[List[Dict[str, Any]]]) -> str:
    """Render ADF text marks (bold, italic, code, links) as Markdown."""
    if not marks:
        return text
    for mark in marks:
        mark_type = mark.get("type")
        if mark_type == "strong":
            text = f"**{text}**"
        elif mark_type == "em":
            text = f"*{text}*"
        elif mark_type == "code":
            text = f"`{text}`"
        elif mark_type == "link":
            href = (mark.get("attrs") or {}).get("href", "")
            text = f"[{text}]({href})" if href else text
        elif mark_type == "strike":
            text = f"~~{text}~~"
    return text


def _inline(node: Any) -> str:
    """Flatten an inline ADF node (or list of them) into a single line."""
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(_inline(child) for child in node)
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get("type", "")
    if node_type == "text":
        return _apply_marks(node.get("text", ""), node.get("marks"))
    if node_type == "hardBreak":
        return "\n"
    if node_type == "inlineCard":
        return (node.get("attrs") or {}).get("url", "")
    if node_type == "mention":
        return (node.get("attrs") or {}).get("text", "")
    if node_type == "emoji":
        return (node.get("attrs") or {}).get("text", "") or (node.get("attrs") or {}).get("shortName", "")
    if node_type in ("media", "mediaInline", "mediaSingle", "mediaGroup"):
        return "[attachment]"
    return _inline(node.get("content"))


def adf_to_text(node: Any, depth: int = 0) -> str:
    """Flatten an ADF document into Markdown-ish text.

    Block nodes append newlines; table rows render as pipe rows so that
    acceptance-criteria tables remain parseable after flattening.
    """
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(adf_to_text(child, depth) for child in node)
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get("type", "")
    content = node.get("content")

    if node_type == "doc":
        return adf_to_text(content, depth).strip()
    if node_type == "paragraph":
        return f"{_inline(content)}\n\n"
    if node_type == "heading":
        level = int((node.get("attrs") or {}).get("level", 1))
        return f"{'#' * max(1, min(level, 6))} {_inline(content)}\n\n"
    if node_type in ("bulletList", "orderedList"):
        lines: List[str] = []
        for index, item in enumerate(content or [], start=1):
            body = adf_to_text(item, depth + 1).strip().replace("\n", " ")
            prefix = f"{index}. " if node_type == "orderedList" else "- "
            lines.append(f"{prefix}{body}")
        return "\n".join(lines) + "\n\n"
    if node_type == "listItem":
        return adf_to_text(content, depth)
    if node_type == "table":
        return adf_to_text(content, depth) + "\n"
    if node_type == "tableRow":
        cells = [_inline(cell.get("content")).strip().replace("\n", " ") for cell in (content or [])]
        return "| " + " | ".join(cells) + " |\n"
    if node_type in ("tableCell", "tableHeader"):
        return _inline(content)
    if node_type == "codeBlock":
        return f"```\n{_inline(content)}\n```\n\n"
    if node_type == "blockquote":
        body = adf_to_text(content, depth).strip()
        return "".join(f"> {line}\n" for line in body.splitlines()) + "\n"
    if node_type == "rule":
        return "---\n\n"
    if node_type in ("mediaSingle", "mediaGroup"):
        return adf_to_text(content, depth)
    if node_type == "inlineCard":
        return _inline(node) + "\n\n"

    return adf_to_text(content, depth)


def flatten_field(value: Any) -> str:
    """Flatten a Jira field that may be ADF JSON, plain text, or a number."""
    if value is None:
        return ""
    if isinstance(value, dict):
        if value.get("type") == "doc":
            return adf_to_text(value)
        for key in _MARKER_KEYS:
            if value.get(key):
                return str(value[key])
        return adf_to_text(value)
    if isinstance(value, list):
        return "\n".join(flatten_field(item) for item in value).strip()
    return str(value).strip()


def _clean_candidate(line: str) -> str:
    """Strip list/table syntax from a captured acceptance-criteria line."""
    text = _LIST_PREFIX.sub("", line).strip()
    if text.startswith("|"):
        cells = [cell.strip() for cell in text.strip("|").split("|")]
        cells = [cell for cell in cells if cell and not _AC_HEADER_CELLS.match(cell)]
        # Drop a leading purely numeric index column.
        if cells and re.fullmatch(r"\d+", cells[0]):
            cells = cells[1:]
        text = " — ".join(cells)
    return text.strip(" -*_`")


def extract_acceptance_criteria(text: str, source: str) -> List[Tuple[str, str]]:
    """Pull acceptance criteria out of a flattened field.

    Returns ``(text, source)`` pairs. Only content under a recognised
    acceptance-criteria heading is captured, so unrelated prose is not
    mistaken for a requirement.
    """
    if not text or not text.strip():
        return []

    lines = text.splitlines()
    captured: List[str] = []
    in_block = False

    for raw in lines:
        line = raw.rstrip()

        if _AC_HEADING.match(line):
            in_block = True
            continue

        if not in_block:
            continue

        stripped = line.strip()
        if not stripped:
            continue
        if _OTHER_HEADING.match(line):
            break
        if _TABLE_SEPARATOR.match(stripped):
            continue

        cleaned = _clean_candidate(line)
        if cleaned:
            captured.append(cleaned)

    results: List[Tuple[str, str]] = []
    for item in captured:
        for piece in re.split(r"\s*(?:;|•)\s+(?=[A-Z0-9])", item):
            piece = piece.strip(" .;-")
            if len(piece) > 3:
                results.append((piece, source))
    return results


def _dedupe(pairs: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    """Assign AC-ids, preserving first-seen source and order."""
    seen: Dict[str, Dict[str, str]] = {}
    for text, source in pairs:
        signature = re.sub(r"\W+", "", text).lower()
        if signature and signature not in seen:
            seen[signature] = {"text": text, "source": source}
    return [
        {"id": f"AC-{index}", "text": item["text"], "source": item["source"]}
        for index, item in enumerate(seen.values(), start=1)
    ]


def normalize_issue(
    issue: Dict[str, Any],
    config: Dict[str, str],
    comments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build the ``TicketContext`` object defined in ``llm.md`` §3.1."""
    fields = issue.get("fields", {}) or {}
    key = issue.get("key", "")

    def name_of(field: str) -> str:
        value = fields.get(field)
        if isinstance(value, dict):
            return str(value.get("name", ""))
        return str(value or "")

    description_text = flatten_field(fields.get("description"))
    comment_payload = comments
    if comment_payload is None:
        comment_payload = ((fields.get("comment") or {}).get("comments")) or []

    normalized_comments: List[Dict[str, str]] = []
    for comment in comment_payload or []:
        author = (comment.get("author") or {}).get("displayName", "")
        normalized_comments.append(
            {
                # Rule R5: no PII — the display name is intentionally not emitted.
                "author_present": bool(author),
                "text": flatten_field(comment.get("body")),
                "created": comment.get("created", ""),
            }
        )

    # --- Acceptance criteria discovery: field → description → comment ---
    ac_pairs: List[Tuple[str, str]] = []

    ac_field_id = (config.get("JIRA_AC_FIELD_ID") or "").strip()
    if ac_field_id and fields.get(ac_field_id):
        ac_pairs.extend(extract_acceptance_criteria(flatten_field(fields[ac_field_id]), "field"))

    if not ac_pairs:
        ac_pairs.extend(extract_acceptance_criteria(description_text, "description"))

    if not ac_pairs:
        for comment in normalized_comments:
            ac_pairs.extend(extract_acceptance_criteria(comment["text"], "comment"))

    return {
        "key": key,
        "summary": str(fields.get("summary", "")).strip(),
        "type": name_of("issuetype"),
        "status": name_of("status"),
        "priority": name_of("priority"),
        "components": [c.get("name", "") for c in fields.get("components") or [] if c.get("name")],
        "labels": list(fields.get("labels") or []),
        "fixVersions": [v.get("name", "") for v in fields.get("fixVersions") or [] if v.get("name")],
        "description_text": description_text,
        "acceptance_criteria": _dedupe(ac_pairs),
        "links": [
            {
                "type": (link.get("type") or {}).get("name", ""),
                "key": (link.get("outwardIssue") or link.get("inwardIssue") or {}).get("key", ""),
            }
            for link in fields.get("issuelinks") or []
        ],
        "attachments": [a.get("filename", "") for a in fields.get("attachment") or [] if a.get("filename")],
        "comments": normalized_comments,
        "source_url": f"{(config.get('JIRA_BASE_URL') or '').rstrip('/')}/browse/{key}" if key else "",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
