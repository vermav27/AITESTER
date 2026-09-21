# llm.md — Project Constitution

> **Protocol 0 artifact — the single source of truth.** When anything conflicts with
> this file, this file wins. It defines the **data schemas**, **behavioral rules**, and
> **architectural invariants** for the *Test Plan Creator from a Jira ID* agent.
>
> Status: **FROZEN v1.0 — 2026-09-22.** The schemas below are implemented and verified
> against live Jira and Ollama. The Halt Rule was satisfied and lifted before any code was
> written into `tools/`; changes to a frozen schema now require a version bump here first.

---

## 1. What this project is (in one paragraph)

An agent that accepts a **Jira issue key** and returns a **review-ready test plan**.
It fetches the ticket deterministically, performs **gap analysis** against a fixed
requirement checklist, drafts a plan with **P0/P1/P2** scenarios traceable to acceptance
criteria or identified gaps, and then **stops at a Human Review Gate**. It never
fabricates requirements and never declares its output final.

**Non-goals:** writing/executing automated test cases, mutating Jira, acting without
human approval.

---

## 2. Architecture — the 3-layer A.N.T. model

> Working definition (**A**gent / **N**avigation / **T**ools); confirm at Blueprint gate.

```
            ┌──────────────────────────────────────────────────────────┐
  JIRA KEY →│  L2 Navigation (deterministic orchestrator)              │
            │  validate key → fetch → normalize → analyze → draft →    │
            │  enforce Review Gate → emit artifacts                    │
            └───────────────┬───────────────────────────┬─────────────┘
                            │ calls                      │ calls
              ┌─────────────▼────────────┐   ┌───────────▼───────────┐
              │ L3 Tools (deterministic) │   │ L1 Agent (reasoning)  │
              │ fetch_jira / fetch_…     │   │ gap analysis,         │
              │ normalize_ticket / …     │   │ scenario derivation,  │
              │ render_plan              │   │ plan drafting         │
              │ no LLM, pure, JSON out   │   │ (non-deterministic)   │
              └──────────────────────────┘   └───────────────────────┘
```

| Layer | Role | Determinism | May call |
|---|---|---|---|
| **L3 — Tools** | I/O + transforms (fetch, parse ADF, render) | Fully deterministic | OS, Jira REST |
| **L2 — Navigation** | Ordering, state, gate enforcement, artifact writing | Deterministic | L3, L1 |
| **L1 — Agent** | Reasoning over the normalized context | Non-deterministic | nothing external |

**Invariant:** the LLM never talks to Jira directly; the tools never contain business
judgement. The JSON schema is the only interface between them.

### 2.1 Implementation map (frozen v1.0)

The engine is a plain importable package (`core/`) so both the web UI and the CLI tools drive the
identical code path. Flask is presentation only.

| Layer | Module | Responsibility |
|---|---|---|
| L3 | `core/config_manager.py` | `.env` load/save, secret masking, config-completeness state |
| L3 | `core/jira_client.py` | Jira REST v3, read-only; retries; structured errors |
| L3 | `core/normalize.py` | ADF → text; `TicketContext`; AC discovery + source tagging |
| L3 | `core/checklist.py` | Deterministic `GapItem[]` from the requirement checklist |
| L3 | `core/ollama_client.py` | Ollama `/api/tags` + `/api/chat` transport |
| L3 | `core/render.py` | `TestPlanDocument` assembly; Markdown + JSON artifacts; review gate |
| L1 | `core/agent.py` | Prompt assembly; plan drafting; section outline from the canonical template |
| L2 | `core/navigation.py` | Orchestration, step trace, review-gate enforcement |
| Presentation | `app/` | Flask factory, blueprints, Jinja templates, static assets |
| L3 CLIs | `tools/` | `_bootstrap`, `fetch_jira`, `fetch_comments`, `normalize_ticket`, `analyze_gaps`, `render_plan`, `verify_connections`, `run_agent` |

**Architectural note:** gap analysis is *split*. The LLM derives scenarios and prose (L1), but the
gaps table itself is computed deterministically (L3) and is the authoritative record. This keeps
rule R1 enforceable even if the model misbehaves.

---

## 3. Data Schemas (frozen interface)

> All fields required unless marked `?`. Timestamps are ISO-8601 UTC.

### 3.1 `TicketContext` — normalized ticket (produced by L3 `normalize_ticket`)
```json
{
  "key": "VWO-123",
  "summary": "string",
  "type": "Story | Bug | Task | ...",
  "status": "string",
  "priority": "Highest | High | Medium | Low | Lowest",
  "components": ["string"],
  "labels": ["string"],
  "fixVersions": ["string"],
  "description_text": "string",
  "acceptance_criteria": [
    { "id": "AC-1", "text": "string", "source": "field | description | comment" }
  ],
  "links": [ { "type": "string", "key": "string" } ],
  "attachments": ["string"],
  "comments": [ { "author?": "string", "text": "string", "created": "ISO-8601" } ],
  "source_url": "string",
  "fetched_at": "ISO-8601"
}
```
**Rules:** `acceptance_criteria[].source` must record where each AC was found. If none
were found, the array is **empty** — never populated by inference.

### 3.2 `GapItem` — one checklist deficiency (produced by L1)
```json
{
  "id": "GAP-001",
  "category": "Functional | Data | NonFunctional | CrossCutting | Clarity",
  "checklist_item": "string",
  "status": "missing | ambiguous",
  "evidence": "string",
  "question": "string",
  "owner?": "string"
}
```
**Rules:** every `ambiguous`/`missing` checklist row becomes exactly one `GapItem`.
`question` must be answerable by the ticket author.

### 3.3 `TestScenario` — one planned test (produced by L1)
```json
{
  "id": "TS-001",
  "title": "string",
  "type": "positive | negative | boundary | cross-role",
  "priority": "P0 | P1 | P2",
  "traces_to": ["AC-1", "GAP-002"],
  "preconditions": ["string"],
  "steps": ["string"],
  "expected": ["string"]
}
```
**Rules:** `traces_to` must be non-empty — a scenario with no AC/GAP link is invalid.
`P0` requires at least one `AC-*` or `GAP-*` reference.

### 3.4 `TestPlanDocument` — final artifact (produced by L3 `render_plan`)
```json
{
  "jira_key": "VWO-123",
  "title": "string",
  "generated_at": "ISO-8601",
  "status": "draft | in_review | approved",
  "scope": { "in": ["string"], "out": ["string"] },
  "gaps": ["GapItem"],
  "scenarios": ["TestScenario"],
  "test_data": ["string"],
  "environment": ["string"],
  "risks": ["string"],
  "entry_criteria": ["string"],
  "exit_criteria": ["string"],
  "review_gate": {
    "pending": true,
    "open_questions": ["string"],
    "summary": "string"
  }
}
```
**Rules:** `status` can never be `final`. `review_gate.pending` must be `true` on any
machine-generated artifact.

**v1.0 additions (implemented in `core/render.py`).** The frozen core above is extended with the
provenance fields the UI and the run index need. All are additive:

| Field | Purpose |
|---|---|
| `model` | Which Ollama model drafted the plan |
| `duration_seconds` | Wall-clock length of the run |
| `source_url` | `{base}/browse/{KEY}` |
| `issue` | `type`, `status`, `priority`, `components`, `labels`, `fixVersions` |
| `acceptance_criteria` | The `AC-*` list, each with its `source` |
| `acceptance_criteria_sources` | Distinct sources seen (`field` / `description` / `comment`) |
| `scenario_count` | Count of drafted scenarios, for the UI summary |
| `draft_body` | The raw model output, kept separate so the deterministic wrapper is reproducible |

`scope`, `test_data`, `environment`, `risks`, `entry_criteria`, and `exit_criteria` are populated
*inside* `draft_body` rather than as structured arrays: a local 4B model does not reliably emit
nested JSON, so asking for Markdown and wrapping it deterministically is the more reliable contract.

---

## 4. Behavioral Rules (the LLM must obey)

| # | Rule |
|---|---|
| **R1** | **Never fabricate ticket content.** A missing AC is a `GapItem`, not a blank to fill. |
| **R2** | **Always end at the Human Review Gate.** Status is `draft`/`in_review`, never `final`. |
| **R3** | **Traceability is mandatory.** Every scenario maps to ≥1 `AC-*` or `GAP-*`. |
| **R4** | **No credentials** — tokens/base URLs never appear in any output. |
| **R5** | **No PII** — never emit the reporter's/author's personal details. |
| **R6** | **Determinism lives in tools.** Fetching/normalizing/rendering never happens in prose. |
| **R7** | **Obey the Halt Rule.** No `tools/` code until Discovery Questions + schema + blueprint are done. |
| **R8** | **Idempotent & resumable.** A re-run for the same key produces the same structured result (prose may vary). |
| **R9** | **Fail loud.** 401/403/404/429/5xx surface clearly; never degrade into an empty plan. |
| **R10** | **Read-only against Jira.** Never transition, comment, or mutate. |
| **R11** | **State your sources.** Record which AC came from field/description/comment. |
| **R12** | **Prioritize by risk.** Classify scenarios `P0` (critical) / `P1` / `P2`; justify P0 via AC/GAP. |

---

## 5. Architectural Invariants

| # | Invariant |
|---|---|
| **I1** | Strict 3-layer separation (Agent / Navigation / Tools); no layer skipping. |
| **I2** | Contract-first: `llm.md` schemas are the interface; both sides validate against them. |
| **I3** | Tools are pure functions of `(env, args) → stdout(JSON)`; no LLM, no side effects beyond stdout/files under the run dir. |
| **I4** | Secrets only from env vars (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`); never persisted. |
| **I5** | Everything is version-controllable text: Markdown artifacts + JSON payloads. |
| **I6** | This file is the single source of truth; conflicts resolve in its favor. |
| **I7** | Output template is fixed (the canonical Test Plan Template); the agent fills it, never reinvents it. |

---

## 6. Tool contracts (names fixed; behavior must match)

| Tool | Input | Output (stdout) | Failure |
|---|---|---|---|
| `fetch_jira` | `KEY` + config | raw issue JSON | non-zero + structured error |
| `fetch_comments` | `KEY` + config | `{"comments": [...], "count": n}` | non-zero + structured error |
| `normalize_ticket` | `KEY` or `--from-stdin` raw issue JSON | `TicketContext` | non-zero + structured error |
| `analyze_gaps` | `KEY` or `--from-stdin` `TicketContext` | `{"key", "summary", "gaps": [GapItem]}` | non-zero + structured error |
| `render_plan` | `--key` + `--draft`, or `--document` / `--from-stdin` `TestPlanDocument` | `{"key","status","gaps","markdown","json","characters"}` | non-zero + structured error |
| `verify_connections` | config only | human report, or `{"ok", "services": [...]}` with `--json` | non-zero if either link fails |
| `run_agent` | prompt string | step trace + artifact path (or full JSON with `--json`) | non-zero + failed step name |

> Structured error shape: `{ "error": true, "http": 403, "message": "...", "key": "VWO-123" }`.

**Config, not env-var mutation:** every tool reads the project `.env` through
`core/config_manager.load_config()` rather than requiring the caller to export variables.
`config_manager` deliberately does not call `load_dotenv()`, which would mutate `os.environ` and
shadow freshly saved values.

---

## 7. End-to-end flow (Navigation)

1. **Validate** `KEY` against `^[A-Z][A-Z0-9]{1,9}-\d{1,6}$` → reject malformed input (no fetch).
   If no key is present, look for a project name and validate the guess against
   `GET /rest/api/3/project/search` before building any JQL.
2. **Fetch** issue + comments.
3. **Normalize** → `TicketContext` (flatten ADF; locate AC).
4. **Analyze** → run checklist → `GapItem[]` (deterministic).
5. **Draft** → derive `TestScenario[]` from AC + gaps, tag priorities (LLM).
6. **Render** → `TestPlanDocument` → Markdown + JSON.
7. **Gate** → attach Human Review Gate; write artifacts; **stop**.

Each step appends to a step trace (`name`, `status`, `detail`) that is returned to the UI, so a
failed run shows exactly how far it got and which step failed.

---

## 8. Output template mapping

The rendered plan follows the canonical `Test_Plan_Template.md`:
`Objective → Scope → Inclusions → Environments → Defect Reporting → Strategy →
Schedule → Deliverables → Entry/Exit → Execution → Closure → Tools → Risks → Approvals`,
with a mandatory **"Gaps & Questions for the author"** section and a **Human Review Gate**
banner (`STATUS: DRAFT — awaiting human review`).

**v1.0 amendment.** Two sections not named by the canonical template are spliced into the outline
immediately after *Test Strategy*: **`Test Scenarios (P0/P1/P2)`** and **`Gaps Summary`**. This was
added because the model otherwise invented its own heading and filed the scenarios under
*Test Execution* (observed in the first live run). The outline is derived from the template file at
prompt-build time, so the two lists cannot drift apart.

The document's actual section order is therefore:

```
Document Information
Acceptance Criteria (as fetched from Jira)   ← deterministic
1. Objective … 6. Test Strategy              ← model
Test Scenarios (P0/P1/P2)                     ← model
Gaps Summary                                  ← model
7. Test Schedule … 15. Appendices             ← model
Gaps & Questions for the author               ← deterministic, authoritative
Human Review Gate                             ← deterministic
```

---

## 9. Open items — resolved

- [x] Confirm A.N.T. layer meanings — **A**gent (L1, `core/agent.py`) / **N**avigation
      (L2, `core/navigation.py`) / **T**ools (L3, `core/*` + `tools/`). Assumption A3 confirmed.
- [x] AC field id / source precedence — custom field → description → comment, source recorded per
      criterion (DQ-3, DQ-6).
- [x] MCP vs REST — no MCP server available; **REST v3** is primary, with `POST /search/jql` for
      search and an explicit 410 message if a v2 endpoint is ever hit (DQ-4).
- [x] Canonical template + delivery target — `templates/Test_Plan_Template.md`; output is local
      `runs/*.md` + `*.json` (DQ-6, DQ-8).
- [x] PROVISIONAL banner removed; schemas frozen at **v1.0**.

---

## 10. Presentation layer (Flask) contracts

The web layer adds no business logic. It is a boundary, and these are its contracts:

| Route | Method | Contract |
|---|---|---|
| `/` | GET | Render the prompt UI, live config state, and the recent `runs/` list |
| `/generate` | POST | `prompt` → `navigation.run()` → render result; `400` on validation failure, `500` on unexpected error |
| `/runs/<filename>` | GET | Download a `.md`/`.json` artifact; any other suffix → `404` |
| `/settings` | GET | Render config with the token masked and installed Ollama models listed |
| `/settings` | POST | Persist non-empty fields to `.env`; blank secrets keep their stored value |
| `/settings/test/jira` | POST | `{"ok": bool, "message": str}`, always HTTP 200 |
| `/settings/test/ollama` | POST | `{"ok": bool, "message": str}`, always HTTP 200 |

**Boundary rules (added in v1.0):**

- **I8** — The UI never calls Jira or Ollama; routes call `core.navigation` (L2) only.
- **I9** — Model output and ticket text are untrusted: raw HTML is neutralized and
  `javascript:`/`data:` URLs are stripped before rendering.
- **I10** — The app binds to `127.0.0.1` with no authentication of its own. It is a local dev
  tool, never a public deployment.
