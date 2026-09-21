"""L1 Agent — reasoning layer.

Turns a normalized ``TicketContext`` plus deterministic ``GapItem`` findings
into a drafted test plan using the local Ollama model. This is the only
non-deterministic module in the project (``llm.md`` §2); everything it is
given is already verified, and everything it returns is treated as a draft
requiring human review (rule R2).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from . import ollama_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = PROJECT_ROOT / "prompts" / "test_plan_prompt.md"
TEMPLATE_FILE = PROJECT_ROOT / "templates" / "Test_Plan_Template.md"

# The skill's mandatory output shape, used when the canonical template is absent.
FALLBACK_SECTIONS: List[str] = [
    "Objective & Scope",
    "Gaps Summary",
    "Test Scenarios (P0/P1/P2)",
    "Test Data & Environment",
    "Risks & Assumptions",
    "Entry / Exit Criteria",
]

# Mandatory sections that the canonical template does not name explicitly.
# They are spliced into the outline so the model has a home for them instead of
# improvising a heading of its own.
EXTRA_SECTIONS: List[Tuple[str, str]] = [
    ("Test Scenarios (P0/P1/P2)", "Test Strategy"),
    ("Gaps Summary", "Test Scenarios"),
]

_SECTION_RE = re.compile(r"^##\s+(\d+\.\s+[^#\n]+?)\s*$", re.MULTILINE)
_FENCE_RE = re.compile(r"^\s*```(?:markdown|md)?\s*\n(.*?)\n\s*```\s*$", re.DOTALL)


class AgentError(Exception):
    """Prompt assembly or drafting failed. Message is user-safe."""


def template_sections() -> List[str]:
    """Extract the canonical test-plan section headings.

    Reading them from ``templates/Test_Plan_Template.md`` keeps the prompt and
    the fixed output template in sync (invariant I7).
    """
    if not TEMPLATE_FILE.exists():
        return list(FALLBACK_SECTIONS)
    headings = _SECTION_RE.findall(TEMPLATE_FILE.read_text(encoding="utf-8"))
    return headings[:15] or list(FALLBACK_SECTIONS)


def section_outline() -> List[str]:
    """Canonical sections plus the mandatory extras, in presentation order."""
    sections = list(template_sections())
    for name, anchor in EXTRA_SECTIONS:
        if any(name.lower() in section.lower() for section in sections):
            continue
        position = len(sections)
        for index, section in enumerate(sections):
            if anchor.lower() in section.lower():
                position = index + 1
                break
        sections.insert(position, name)
    return sections


def _load_prompt_template() -> str:
    if not PROMPT_FILE.exists():
        raise AgentError(f"Prompt file not found: {PROMPT_FILE.name}. Expected it under prompts/.")
    return PROMPT_FILE.read_text(encoding="utf-8")


def render_ticket_context(ticket: Dict[str, Any]) -> str:
    """Render the TicketContext as the plain-text block the LLM reads."""
    criteria = ticket.get("acceptance_criteria") or []
    if criteria:
        ac_block = "\n".join(
            f"{item['id']} (source: {item['source']}): {item['text']}" for item in criteria
        )
    else:
        ac_block = (
            "NONE FOUND. Acceptance criteria are absent from the custom field, the description, "
            "and the comments. Do not invent any."
        )

    comments = ticket.get("comments") or []
    if comments:
        comment_block = "\n\n".join(
            f"--- comment {index} ---\n{comment.get('text', '')[:1500]}"
            for index, comment in enumerate(comments[:5], start=1)
        )
    else:
        comment_block = "(no comments)"

    links = ticket.get("links") or []
    link_block = "\n".join(f"- {link.get('type')}: {link.get('key')}" for link in links) or "(none)"

    return "\n".join(
        [
            f"Key: {ticket.get('key')}",
            f"Summary: {ticket.get('summary')}",
            f"Issue Type: {ticket.get('type')}",
            f"Status: {ticket.get('status')}",
            f"Priority: {ticket.get('priority')}",
            f"Components: {', '.join(ticket.get('components') or []) or 'none'}",
            f"Labels: {', '.join(ticket.get('labels') or []) or 'none'}",
            f"Fix Versions: {', '.join(ticket.get('fixVersions') or []) or 'none'}",
            "",
            "Description:",
            (ticket.get("description_text") or "(empty)").strip() or "(empty)",
            "",
            "Acceptance Criteria (already extracted — use these ids):",
            ac_block,
            "",
            "Linked Issues:",
            link_block,
            "",
            "Comments:",
            comment_block,
        ]
    )


def render_gap_table(gaps: List[Dict[str, str]]) -> str:
    """Render gaps as a compact table the model can reference by id."""
    if not gaps:
        return "No gaps detected — every checklist item has evidence in the ticket."
    lines = ["| id | category | status | checklist item | question for the author |", "|---|---|---|---|---|"]
    for gap in gaps:
        lines.append(
            f"| {gap['id']} | {gap['category']} | {gap['status']} | "
            f"{gap['checklist_item']} | {gap['question']} |"
        )
    return "\n".join(lines)


def build_messages(ticket: Dict[str, Any], gaps: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Assemble the system + user messages for Ollama."""
    prompt = _load_prompt_template()

    section_outline_text = "\n".join(f"## {heading}" for heading in section_outline())

    system = (
        "You are a senior QA engineer writing a test plan draft from a single Jira ticket. "
        "You only use facts present in the supplied ticket context. You never invent acceptance "
        "criteria, requirements, or ticket content. Every test scenario must be traceable to an "
        "AC-* or GAP-* id. You output GitHub-flavoured Markdown only — no preamble, no code fences "
        "around the whole document, no closing commentary."
    )

    user = (
        prompt.replace("{{TICKET_CONTEXT}}", render_ticket_context(ticket))
        .replace("{{GAP_TABLE}}", render_gap_table(gaps))
        .replace("{{SECTION_OUTLINE}}", section_outline_text)
        .replace("{{KEY}}", ticket.get("key", ""))
        .replace("{{TITLE}}", ticket.get("summary", ""))
    )

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def strip_wrapping_fence(text: str) -> str:
    """Remove a ```-fence the model may have wrapped the whole document in."""
    match = _FENCE_RE.match(text.strip())
    return match.group(1).strip() if match else text.strip()


def draft_plan(
    ticket: Dict[str, Any], gaps: List[Dict[str, str]], config: Dict[str, str]
) -> Tuple[str, str]:
    """Draft the plan body. Returns ``(markdown, model_used)``."""
    messages = build_messages(ticket, gaps)
    model = (config.get("OLLAMA_MODEL") or "unknown").strip()
    body = ollama_client.chat(messages, config)
    return strip_wrapping_fence(body), model
