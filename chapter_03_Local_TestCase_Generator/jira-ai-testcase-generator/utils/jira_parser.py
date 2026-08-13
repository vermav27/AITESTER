"""Parse a Jira issue JSON payload into clean, structured requirement text.

The Jira REST API returns a deeply nested payload. This module extracts only
the fields the QA pipeline needs and tolerates missing fields — the generated
requirement block never invents content that is not present in the ticket.
"""

from __future__ import annotations

import re
from typing import Dict, List

_AC_HEADINGS = re.compile(
    r"^\s*(acceptance\s*criteria|acceptance\s*test|done\s*when|definition\s*of\s*done)\s*[:#*\-]*\s*$",
    re.IGNORECASE,
)


def _clean_plain_text(value: str) -> str:
    """Strip basic ADF markup so description text reads cleanly.

    Jira descriptions can be Atlassian Document Format (ADF) JSON or simple
    wiki markup. For non-JSON strings we strip the most common wiki markers.
    """
    if not value:
        return ""
    text = re.sub(r"h[1-6]\.", "", value)
    text = re.sub(r"[*_~^{}]", "", text)
    text = text.replace("----", "").replace("---", "").replace("||", " | ")
    return text.strip()


def _extract_adf_text(adf: Dict) -> str:
    """Extract plain text from an Atlassian Document Format (ADF) node."""
    parts: List[str] = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text" and node.get("text"):
                parts.append(node["text"])
            for child in node.get("content", []):
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(adf)
    return "\n".join(parts).strip()


def _split_acceptance_criteria(description: str) -> str:
    """Return the acceptance-criteria section of a wiki-markup description.

    Looks for a heading such as "Acceptance Criteria:" followed by lines of
    requirements. Returns "Not specified" when no such section exists.
    """
    if not description:
        return "Not specified"

    lines = description.splitlines()
    section: List[str] = []
    capture = False
    for line in lines:
        if _AC_HEADINGS.match(line):
            capture = True
            continue
        if capture:
            if re.match(r"^\s*(h[1-6]\.|[a-z][a-z\s]+:)", line) and not line.strip().startswith(("-", "*", "1.")):
                break
            if line.strip():
                section.append(line.strip())
    if not section:
        return "Not specified"
    return "\n".join(section)


def parse_issue(issue: Dict, config: Dict[str, str]) -> Dict[str, str]:
    """Convert a Jira issue dict into a requirements block for the LLM.

    Returns a dict with ``summary``, ``description``, ``acceptance_criteria``,
    ``issue_type``, ``priority``, ``status``, ``labels``, ``components`` and a
    pre-formatted ``requirement_context`` string.
    """
    fields = issue.get("fields", {})

    summary = _clean_plain_text(str(fields.get("summary", "")))
    description = fields.get("description", "") or ""
    if isinstance(description, dict):
        description = _extract_adf_text(description)
    else:
        description = _clean_plain_text(str(description))

    # Acceptance criteria: prefer the configured custom field, then parse the
    # description for an "Acceptance Criteria" section, else mark unspecified.
    custom_field = config.get("ACCEPTANCE_CRITERIA_FIELD_ID", "").strip()
    acceptance = "Not specified"
    if custom_field and fields.get(custom_field):
        raw = fields[custom_field]
        if isinstance(raw, dict):
            acceptance = _extract_adf_text(raw)
        else:
            acceptance = _clean_plain_text(str(raw))
    elif description:
        acceptance = _split_acceptance_criteria(description)

    issue_type = fields.get("issuetype", {}).get("name", "Not specified")
    priority = fields.get("priority", {}).get("name", "Not specified")
    status = fields.get("status", {}).get("name", "Not specified")

    labels = fields.get("labels", []) or []
    components = [c.get("name", "") for c in fields.get("components", []) or [] if c.get("name")]

    key = issue.get("key", "Not specified")
    requirement_context = (
        f"Jira ID: {key}\n\n"
        f"Summary:\n{summary}\n\n"
        f"Description:\n{description}\n\n"
        f"Acceptance Criteria:\n{acceptance}\n\n"
        f"Issue Type: {issue_type}\n"
        f"Priority: {priority}\n"
        f"Status: {status}\n"
        f"Labels: {', '.join(labels) if labels else 'Not specified'}\n"
        f"Components: {', '.join(components) if components else 'Not specified'}"
    )

    return {
        "key": key,
        "summary": summary,
        "description": description,
        "acceptance_criteria": acceptance,
        "issue_type": issue_type,
        "priority": priority,
        "status": status,
        "labels": labels,
        "components": components,
        "requirement_context": requirement_context,
    }
