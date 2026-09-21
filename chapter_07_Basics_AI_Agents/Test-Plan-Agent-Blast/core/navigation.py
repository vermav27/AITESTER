"""L2 Navigation — the deterministic orchestrator.

This is the reasoning-free routing layer from ``llm.md`` §2: it validates the
request, orders the tool calls, enforces the Human Review Gate, and writes the
run artifacts. It never talks to Jira or the LLM directly — it calls L3 tools
and the L1 agent and passes JSON between them.

End-to-end flow (``llm.md`` §7):
validate → fetch → normalize → analyse → draft → render → gate → stop.
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable, Dict, List, Optional

from . import agent, checklist, config_manager, jira_client, normalize, ollama_client, render

JIRA_KEY_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d{1,6})\b")
PROJECT_PATTERNS = [
    re.compile(r"\bproject\s*[=:]?\s*\"?([A-Z][A-Z0-9]{1,9})\"?", re.IGNORECASE),
    re.compile(r"\b([A-Z][A-Z0-9]{1,9})\s+project\b", re.IGNORECASE),
    re.compile(r"\bin\s+\"?([A-Z][A-Z0-9]{1,9})\"?\b", re.IGNORECASE),
]

# Words that look like a project key but are not one.
_STOP_WORDS = {"A", "AN", "THE", "AND", "FOR", "NEW", "LATEST", "TEST", "PLAN", "THIS", "THAT", "PLEASE"}


class NavigationError(Exception):
    """A pipeline step failed. ``step`` names it; ``message`` is user-safe."""

    def __init__(self, step: str, message: str):
        super().__init__(message)
        self.step = step
        self.message = message
        self.steps: List[Dict[str, str]] = []


class Steps:
    """Collects a human-readable trace of what the pipeline actually did."""

    def __init__(self) -> None:
        self._items: List[Dict[str, str]] = []

    def start(self, name: str) -> None:
        self._items.append({"name": name, "status": "running", "detail": ""})

    def done(self, detail: str) -> None:
        if self._items:
            self._items[-1]["status"] = "done"
            self._items[-1]["detail"] = detail

    def failed(self, detail: str) -> None:
        if self._items:
            self._items[-1]["status"] = "failed"
            self._items[-1]["detail"] = detail

    def as_list(self) -> List[Dict[str, str]]:
        return list(self._items)


def extract_jira_key(text: str) -> Optional[str]:
    """Return the first Jira issue key in ``text``, if any."""
    match = JIRA_KEY_PATTERN.search(text.upper())
    return match.group(1) if match else None


def extract_project_key(text: str) -> Optional[str]:
    """Return a project key mentioned in ``text`` when no issue key is present."""
    upper = text.upper()
    for pattern in PROJECT_PATTERNS:
        for match in pattern.finditer(upper):
            candidate = match.group(1)
            if candidate not in _STOP_WORDS and not re.fullmatch(r"\d+", candidate):
                return candidate
    return None


def resolve_project_key(candidate: str, config: Dict[str, str]) -> str:
    """Confirm a guessed project key exists before building any JQL.

    Natural-language prompts produce loose candidates ("in the QA project" →
    "QA"), so the guess is validated against the projects this account can
    actually see. A bad guess becomes a helpful error instead of a confusing
    empty search result.
    """
    try:
        projects = jira_client.list_projects(config)
    except jira_client.JiraError as exc:
        raise NavigationError("resolve", exc.message)

    accessible = {project["key"].upper(): project["key"] for project in projects}
    if candidate.upper() in accessible:
        return accessible[candidate.upper()]

    available = ", ".join(sorted(accessible)) or "none"
    raise NavigationError(
        "resolve",
        f"Project '{candidate}' was not found or is not accessible with these credentials. "
        f"Projects available to this account: {available}.",
    )


def _require_configuration(config: Dict[str, str]) -> None:
    state = config_manager.connection_state(config)
    if not state["jira_configured"]:
        raise NavigationError(
            "config",
            "Jira is not configured. Add the Base URL, Email and API token on the Settings page.",
        )
    if not state["ollama_configured"]:
        raise NavigationError("config", "Ollama is not configured. Set the Ollama URL on the Settings page.")


def _resolve_key(
    prompt_text: str, config: Dict[str, str], steps: Steps
) -> str:
    """Decide which ticket the request refers to (flow step 1)."""
    steps.start("Resolve target ticket")
    requested_key = extract_jira_key(prompt_text)
    if requested_key:
        steps.done(f"Using the issue key found in the prompt: {requested_key}")
        return requested_key

    project_key = extract_project_key(prompt_text)
    if not project_key:
        raise NavigationError(
            "resolve",
            "No Jira issue key found in your request. Include a key such as 'KAN-1', "
            "or name a project to use its latest ticket (e.g. 'latest ticket in <PROJECT>').",
        )

    project_key = resolve_project_key(project_key, config)
    try:
        issue_key = jira_client.latest_issue_key(project_key, config)
    except jira_client.JiraError as exc:
        raise NavigationError("resolve", exc.message)
    steps.done(f"No key in the prompt; resolved the latest ticket in {project_key}: {issue_key}")
    return issue_key


def _execute(
    prompt_text: str,
    config: Dict[str, str],
    steps: Steps,
    note: Callable[[str], None],
) -> Dict[str, Any]:
    """Run the pipeline. Raises :class:`NavigationError` on the first failure."""
    started = time.perf_counter()

    issue_key = _resolve_key(prompt_text, config, steps)

    # 2. Fetch the issue and its comments ----------------------------------
    steps.start("Fetch ticket from Jira")
    note(f"Fetching {issue_key} from Jira…")
    try:
        raw_issue = jira_client.fetch_issue(issue_key, config)
        comments = jira_client.fetch_comments(issue_key, config)
    except jira_client.JiraError as exc:
        raise NavigationError("fetch", exc.message)
    steps.done(f"Fetched {issue_key} and {len(comments)} comment(s) over REST API v3")

    # 3. Normalize into TicketContext --------------------------------------
    steps.start("Normalize ticket")
    note("Normalizing ticket fields…")
    ticket = normalize.normalize_issue(raw_issue, config, comments)
    ac_count = len(ticket["acceptance_criteria"])
    ac_sources = ", ".join(sorted({ac["source"] for ac in ticket["acceptance_criteria"]})) or "none found"
    steps.done(f"Extracted {ac_count} acceptance criteria (source: {ac_sources})")

    # 4. Deterministic gap analysis ----------------------------------------
    steps.start("Analyze requirement gaps")
    note("Running the requirement checklist…")
    gaps = checklist.analyze_gaps(ticket)
    steps.done(checklist.summarize_gaps(gaps))

    # 5. Draft with the local model (L1) -----------------------------------
    steps.start("Draft plan with Ollama")
    note(f"Drafting the test plan with {config.get('OLLAMA_MODEL')}…")
    try:
        draft_body, model = agent.draft_plan(ticket, gaps, config)
    except (ollama_client.OllamaError, agent.AgentError) as exc:
        raise NavigationError("draft", str(exc))
    steps.done(f"Drafted {len(draft_body):,} characters with {model}")

    # 6. Render + persist artifacts, then stop at the gate -----------------
    steps.start("Render plan and stop at review gate")
    note("Rendering the plan…")
    duration = time.perf_counter() - started
    document = render.build_document(ticket, gaps, draft_body, model, duration)
    markdown, artifacts = render.render_and_write(document)
    steps.done(f"Wrote {artifacts['markdown_name']} — DRAFT, awaiting human review")

    return {
        "ok": True,
        "key": ticket["key"],
        "title": ticket["summary"],
        "status": "draft",
        "model": model,
        "duration_seconds": document["duration_seconds"],
        "steps": steps.as_list(),
        "ticket": ticket,
        "gaps": gaps,
        "gap_count": len(gaps),
        "acceptance_criteria_count": ac_count,
        "scenario_count": document["scenario_count"],
        "review_gate": document["review_gate"],
        "plan_markdown": markdown,
        "artifacts": artifacts,
    }


def run(
    prompt_text: str,
    config: Optional[Dict[str, str]] = None,
    progress: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Execute the full pipeline for a natural-language request.

    Returns a JSON-serializable payload for the UI — including the rendered
    plan and the paths of the written artifacts. Raises
    :class:`NavigationError`, which carries the step trace for the UI.
    """
    config = config or config_manager.load_config()
    steps = Steps()

    def note(message: str) -> None:
        if progress:
            progress(message)

    try:
        _require_configuration(config)
        return _execute(prompt_text, config, steps, note)
    except NavigationError as exc:
        if not exc.steps:
            exc.steps = steps.as_list()
        raise
