"""L3 tool — deterministic requirement gap analysis.

Runs the normalized ticket through the requirement checklist from
``templates/requirement-checklist.md`` using evidence-based keyword detection,
then emits one ``GapItem`` (``llm.md`` §3.2) per deficiency.

This is the deterministic half of the gap analysis. It never invents a
requirement and never judges quality — it reports what the ticket does not
state, and what it states ambiguously, so the LLM layer has grounded input and
the tester has concrete questions to ask (rule R1).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Pattern, Tuple

# --- Checklist definition -------------------------------------------------
# ``patterns``: any match means the ticket provides evidence for this item.
# ``question``: what to ask the author when the evidence is absent.
CHECKS: List[Dict[str, Any]] = [
    {
        "category": "Functional",
        "item": "Clear user story / goal",
        "patterns": [r"\bas a\b.{0,80}\bi (?:want|need|should)\b", r"\buser story\b", r"\bgoal\b", r"\bpurpose\b", r"\bobjective\b"],
        "question": "The user story or goal is not stated. Who is the actor and what outcome do they need?",
    },
    {
        "category": "Functional",
        "item": "Happy path fully described",
        "patterns": [r"\bhappy path\b", r"\bsuccess(?:ful|fully)?\b", r"\bmain flow\b", r"\bprimary flow\b", r"\bend[- ]to[- ]end\b"],
        "question": "The expected success flow is not described. What is the end-to-end happy path?",
    },
    {
        "category": "Functional",
        "item": "Negative / error paths described",
        "patterns": [r"\berror\b", r"\binvalid\b", r"\bfail(?:s|ure|ed)?\b", r"\breject\b", r"\bnegative\b", r"\bunauthori[sz]ed\b", r"\bexception\b", r"\bnot allowed\b"],
        "question": "No error or negative path is described. What should happen for invalid input, failure responses, and lack of permission?",
    },
    {
        "category": "Functional",
        "item": "Boundary & empty states covered",
        "patterns": [r"\bboundar", r"\bempty\b", r"\bzero\b", r"\bmaximum\b", r"\bminimum\b", r"\bmax\b", r"\bmin\b", r"\blimit\b", r"\bnull\b", r"\bblank\b", r"\bno (?:data|records?|results?)\b"],
        "question": "Boundary and empty states are not specified. What are the min, max, zero/empty, and null behaviours?",
    },
    {
        "category": "Functional",
        "item": "State transitions / workflow steps enumerated",
        "patterns": [r"\bstep\s*\d", r"\bflow\b", r"\btransition", r"\bstatus\b", r"\bworkflow\b", r"\bthen\b"],
        "question": "The workflow is not enumerated. What are the ordered steps and allowed state transitions?",
    },
    {
        "category": "Data",
        "item": "Required test data specified or derivable",
        "patterns": [r"\btest data\b", r"\bsample\b", r"\bfixture", r"\bseed\b", r"\bdata ?set\b", r"\bexample (?:data|payload|record)\b", r"\bpayload\b"],
        "question": "No test data is specified. What input data (accounts, records, payloads) is required to test this?",
    },
    {
        "category": "Data",
        "item": "Environment / config / feature flags named",
        "patterns": [r"\benvironment\b", r"\benv\b", r"\bconfig", r"\bfeature flag\b", r"\btoggle\b", r"\bstaging\b", r"\bqa\b", r"\buat\b", r"\burl\b", r"\btenant\b"],
        "question": "The target environment or configuration is not named. Which environment and feature flags apply?",
    },
    {
        "category": "Data",
        "item": "External dependencies & integrations listed",
        "patterns": [r"\bapi\b", r"\bintegrat", r"\bdependen", r"\bthird[- ]party\b", r"\bwebhook\b", r"\bendpoint\b", r"\bservice\b"],
        "question": "External dependencies are not listed. Which APIs, services, or integrations does this depend on?",
    },
    {
        "category": "Data",
        "item": "Preconditions / setup stated",
        "patterns": [r"\bprecondition", r"\bprerequisite", r"\bsetup\b", r"\bset up\b", r"\bgiven\b", r"\brequire[sd]?\b", r"\bbefore testing\b"],
        "question": "Preconditions are not stated. What setup, account state, or permissions must exist before testing?",
    },
    {
        "category": "NonFunctional",
        "item": "Performance / load expectations",
        "patterns": [r"\bperformance\b", r"\blatency\b", r"\bresponse time\b", r"\bthroughput\b", r"\bload\b", r"\bconcurren", r"\bscal", r"\btimeout\b", r"\b\d+\s?(?:ms|milliseconds|seconds|secs)\b"],
        "question": "No performance expectation is given. What response time, throughput, or concurrency must hold?",
    },
    {
        "category": "NonFunctional",
        "item": "Security / authorization (which roles can and cannot)",
        "patterns": [r"\bsecurity\b", r"\bauthoriz", r"\bpermission", r"\brole", r"\baccess control\b", r"\bauthenticat", r"\bencrypt", r"\bprivilege", r"\brbac\b"],
        "question": "Authorization rules are not defined. Which roles can and cannot perform this action?",
    },
    {
        "category": "NonFunctional",
        "item": "Accessibility (a11y) expectations",
        "patterns": [r"\baccessib", r"\ba11y\b", r"\bwcag\b", r"\bscreen reader\b", r"\bkeyboard\b", r"\baria\b", r"\bcontrast\b", r"\balt text\b"],
        "question": "No accessibility expectation is stated. Are WCAG levels, keyboard navigation, or screen-reader support required?",
    },
    {
        "category": "NonFunctional",
        "item": "Internationalization / localization",
        "patterns": [r"\bi18n\b", r"\bl10n\b", r"\blocali[sz]", r"\btranslat", r"\blanguage\b", r"\blocale\b", r"\btimezone\b", r"\bcurrency\b"],
        "question": "Localization is not addressed. Are multiple languages, locales, timezones, or date/number formats in scope?",
    },
    {
        "category": "NonFunctional",
        "item": "Audit / logging / observability",
        "patterns": [r"\baudit\b", r"\blog", r"\bmonitor", r"\bobservab", r"\bmetric", r"\balert", r"\btrace\b", r"\btelemetry\b"],
        "question": "Logging and observability are not specified. What should be logged, and which alerts or metrics matter?",
    },
    {
        "category": "CrossCutting",
        "item": "Impact on existing features (regression surface)",
        "patterns": [r"\bregression\b", r"\bexisting\b", r"\bimpact", r"\baffected\b", r"\bdownstream\b", r"\bside effect"],
        "question": "The regression surface is unclear. Which existing features or flows could this change affect?",
    },
    {
        "category": "CrossCutting",
        "item": "Backward compatibility / migration",
        "patterns": [r"\bmigrat", r"\bbackward compat", r"\bcompatib", r"\bdeprecat", r"\bold data\b", r"\blegacy\b"],
        "question": "Backward compatibility is not addressed. Is there existing data or an old behaviour that must keep working?",
    },
    {
        "category": "CrossCutting",
        "item": "Mobile / responsive / browser matrix",
        "patterns": [r"\bmobile\b", r"\bresponsive\b", r"\bbrowser", r"\bchrome\b", r"\bsafari\b", r"\bfirefox\b", r"\bedge\b", r"\btablet\b", r"\bviewport\b", r"\bios\b", r"\bandroid\b", r"\bscreen size\b"],
        "question": "The device and browser matrix is missing. Which browsers, screen sizes, or platforms must be covered?",
    },
    {
        "category": "CrossCutting",
        "item": "Rollback / feature-flag behaviour",
        "patterns": [r"\brollback\b", r"\broll back\b", r"\brevert\b", r"\bkill switch\b", r"\bfallback\b", r"\bdisable\b", r"\bflag off\b"],
        "question": "Rollback behaviour is not described. How is this feature disabled or reverted if it fails in production?",
    },
    {
        "category": "Clarity",
        "item": "Terms defined consistently",
        "patterns": [r"\bglossary\b", r"\bdefinition\b", r"\babbreviation", r"\bacronym", r"\bterminolog"],
        "question": "Key terms are not defined. Can you define the domain terms used in this ticket?",
    },
    {
        "category": "Clarity",
        "item": "Mockups / designs linked and consistent",
        "patterns": [r"\bfigma\b", r"\bmockup", r"\bdesign\b", r"\bwireframe", r"\bprototype\b", r"\bscreenshot", r"\battachment\b"],
        "question": "No design is linked. Is there a mockup or spec the expected UI/API shape should match?",
    },
]

# Words that make a requirement untestable, with the question they raise.
AMBIGUITY_MARKERS: List[Tuple[str, Pattern[str], str]] = [
    (r"\bTBD\b|\bTBC\b|to be (?:decided|confirmed|determined)", re.compile(r"\bTBD\b|\bTBC\b|to be (?:decided|confirmed|determined)", re.IGNORECASE), "An open placeholder (TBD/TBC) is still in the ticket. Can it be resolved before testing starts?"),
    (r"\betc\b|and so on", re.compile(r"\betc\.?\b|and so on", re.IGNORECASE), "'etc.' leaves the list open-ended. Can the full list be enumerated?"),
    (r"handle gracefully|graceful", re.compile(r"handle[d]? gracefully", re.IGNORECASE), "'Handle gracefully' is not testable. What exactly should the user see?"),
    (r"as appropriate|if needed|as needed|when required", re.compile(r"as appropriate|if (?:needed|required|applicable)|as needed|where applicable", re.IGNORECASE), "A conditional requirement is vague. Under exactly which conditions does it apply?"),
    (r"should probably|might|could|possibly", re.compile(r"should probably|\bmight\b|\bpossibly\b", re.IGNORECASE), "Hedged wording makes the expected result unclear. Is this behaviour required or optional?"),
    (r"user-friendly|intuitive|properly|correctly|fast|seamless", re.compile(r"user[- ]friendly|\bintuitive\b|\bproperly\b|\bcorrectly\b|\bfast\b|\bseamless\b|\breasonable\b", re.IGNORECASE), "This quality word has no pass/fail threshold. What is the measurable expectation?"),
]

_SNIPPET_RADIUS = 60


def build_corpus(ticket: Dict[str, Any]) -> str:
    """Assemble every testable piece of the ticket into one searchable string."""
    parts: List[str] = [
        ticket.get("summary", ""),
        ticket.get("description_text", ""),
    ]
    for criterion in ticket.get("acceptance_criteria", []) or []:
        parts.append(criterion.get("text", ""))
    for comment in ticket.get("comments", []) or []:
        parts.append(comment.get("text", ""))
    parts.extend(ticket.get("labels", []) or [])
    parts.extend(ticket.get("components", []) or [])
    return "\n".join(part for part in parts if part)


def _first_match(corpus: str, patterns: List[str]) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, corpus, re.IGNORECASE)
        if match:
            return _snippet(corpus, match.start(), match.end())
    return None


def _snippet(corpus: str, start: int, end: int) -> str:
    left = max(0, start - _SNIPPET_RADIUS)
    right = min(len(corpus), end + _SNIPPET_RADIUS)
    return re.sub(r"\s+", " ", corpus[left:right]).strip()


def analyze_gaps(ticket: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return ``GapItem`` dicts for everything the ticket fails to state."""
    corpus = build_corpus(ticket)
    raw: List[Dict[str, str]] = []

    # The single most important check: are there acceptance criteria at all?
    if not (ticket.get("acceptance_criteria") or []):
        raw.append(
            {
                "category": "Functional",
                "checklist_item": "Acceptance criteria are testable (observable pass/fail)",
                "status": "missing",
                "evidence": "No acceptance criteria found in the custom field, the description, or the comments.",
                "question": "Could you add testable acceptance criteria (an observable pass/fail per requirement)?",
            }
        )

    for check in CHECKS:
        if _first_match(corpus, check["patterns"]) is None:
            raw.append(
                {
                    "category": check["category"],
                    "checklist_item": check["item"],
                    "status": "missing",
                    "evidence": "Not stated anywhere in the ticket.",
                    "question": check["question"],
                }
            )

    seen_markers: set = set()
    for _, pattern, question in AMBIGUITY_MARKERS:
        match = pattern.search(corpus)
        if match and question not in seen_markers:
            seen_markers.add(question)
            raw.append(
                {
                    "category": "Clarity",
                    "checklist_item": f"Ambiguous wording: '{match.group(0)}'",
                    "status": "ambiguous",
                    "evidence": _snippet(corpus, match.start(), match.end()),
                    "question": question,
                }
            )

    for index, gap in enumerate(raw, start=1):
        gap["id"] = f"GAP-{index:03d}"
    return raw


def summarize_gaps(gaps: List[Dict[str, str]]) -> str:
    """One-line summary used in the UI and the run log."""
    if not gaps:
        return "No gaps found — every checklist item has evidence in the ticket."
    missing = sum(1 for gap in gaps if gap["status"] == "missing")
    ambiguous = len(gaps) - missing
    return f"{len(gaps)} gap(s): {missing} missing, {ambiguous} ambiguous."
