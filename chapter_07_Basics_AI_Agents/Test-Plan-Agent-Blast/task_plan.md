# task_plan.md — Test Plan Creator from a Jira ID

> **Protocol 0 artifact.** This file holds phases, goals, and checklists only.
> Research lives in `findings.md`, the run log in `progress.md`, and the frozen
> contract (schemas / rules / invariants) in `llm.md`.
>
> Governed by `BLAST.md` (Protocol 0 → mandatory initialization, then halt).

---

## 1. Mission

Build a **deterministic, self-healing agent** that takes a single **Jira issue key**
(e.g. `VWO-123`) and produces a **review-ready test plan** that a human must approve.

The agent is a **drafting + gap-analysis assistant**, never an autopilot. Success is a
plan a tester can sign off on — not a plan the agent declares "done".

**Primary input:** `JIRA-KEY` (regex `^[A-Z][A-Z0-9]*-\d+$`)
**Primary output:** `test_plan_<JIRA-KEY>.md` (Markdown, based on the Test Plan Template)

---

## 2. Definition of Done (project level)

- [ ] Given a Jira key, the agent fetches the ticket deterministically (no guessing).
- [ ] The agent produces a **Gaps & Questions for the author** section (the highest-value output).
- [ ] The agent drafts a full test plan with **P0/P1/P2** scenarios traceable to an AC or a GAP.
- [ ] The run always ends at a **Human Review Gate** (status = `draft` / `in_review`, never `final`).
- [ ] No credentials, tokens, or PII of the reporter/author appear in any artifact.
- [ ] Every step is reproducible from `llm.md` + `tools/` with no hidden state.
- [ ] `llm.md` schema is frozen and referenced by both the agent and the tools.

---

## 3. Phase Map (B.L.A.S.T.)

| Phase | BLAST stage | Goal | Status |
|---|---|---|---|
| **0** | Initialization | Project memory + constitution (`task_plan.md`, `findings.md`, `progress.md`, `llm.md`) | ✅ Done |
| 1 | **B**lueprint | Freeze data schemas, tools list, acceptance tests for the agent itself | ✅ Done |
| 2 | **L**ink | Wire Jira fetch; prove auth and field mapping end-to-end | ✅ Done |
| 3 | **A**rchitect | Build the 3-layer pipeline (Agent / Navigation / Tools) | ✅ Done |
| 4 | **S**tylize | Harden output format, error surfaces, prompts, review gate UX | ✅ Done |
| 5 | **T**rigger | Schedule / event trigger; self-healing retries; monitoring | ⬜ Not started |

> **Protocol 0 Halt Rule:** satisfied — Discovery Questions answered, schema frozen, blueprint
> approved. `tools/` code was written only after those three conditions were met (01:05 IST).

### Delivered artifacts (Phases 1-4)

| Area | Path |
|---|---|
| Flask entry point | `run.py` |
| Flask app (factory + blueprints + templates + static) | `app/` |
| Deterministic engine (L3) + agent (L1) + orchestrator (L2) | `core/` |
| B.L.A.S.T. L3 CLIs | `tools/` |
| Layer-1 SOPs | `architecture/` |
| Pinned drafting prompt | `prompts/test_plan_prompt.md` |
| Canonical template + checklist | `templates/` |
| Generated plans | `runs/` |

---

## 4. Phase 0 — Initialization checklist (complete)

- [x] Read `BLAST.md` and confirm Protocol 0 requirements.
- [x] Capture the objective (test plan creator from a Jira ID).
- [x] Create `task_plan.md` (this file).
- [x] Create `findings.md` with Jira research + request examples.
- [x] Create `progress.md` with a timestamped run log.
- [x] Create `llm.md` as the Project Constitution (schemas / rules / invariants).
- [x] Get **Blueprint approved** (Phase 1 gate).
- [x] Answer the Discovery Questions in §5.
- [x] Freeze the Data Schema in `llm.md` (provisional banner removed).

---

## 5. Discovery Questions (answered)

| # | Question | Why it matters | Answer |
|---|---|---|---|
| DQ-1 | **Atlassian Cloud or Server/Data Center?** | Auth mode + API path. | **Cloud, REST API v3.** v2 is removed on this instance (410). Basic auth with email + API token. |
| DQ-2 | Which **Jira project(s)** are in scope? | Search rules, sample tickets. | Projects visible to this account: **KAN**, **SAM1**. Sample tickets: `KAN-1` (login page story), `KAN-5` (latest in KAN). |
| DQ-3 | Where do **acceptance criteria** live? | Which fields to fetch. | *Not standardized.* Resolved by design: check the configured custom field → description heading → comment, and record the source. `KAN-1` has none, which the agent reports rather than invents. |
| DQ-4 | Is a **Jira MCP server** available? | Preferred path vs REST. | Not available. **REST v3 is the primary path** (`core/jira_client.py`). |
| DQ-5 | Are **Confluence** pages in scope? | Whether to add `fetch_confluence`. | **Out of scope for v1.** |
| DQ-6 | Which **template** is canonical? | Output shape. | The bundled `Test_Plan_Template.md` (copied to `templates/`), with mandatory added `Test Scenarios` and `Gaps Summary` sections. |
| DQ-7 | **Environments / test data / roles** available? | Honest Environment/Data sections. | Unknown per ticket. Handled by design: the prompt requires clearly-labelled placeholders such as `[QA environment — confirm]` instead of invented specifics. |
| DQ-8 | Where does the output go? | Triggers + delivery. | **Local files in `runs/`** (`.md` + `.json`), downloadable from the UI. Delivery to Confluence/Slack is a Phase 5 concern. |
| DQ-9 | Any **compliance/redaction** rules? | Hard output constraints. | No credentials in any artifact; no reporter/author PII (implemented in `normalize_issue`). |

---

## 6. Phase 1 — Blueprint checklist (complete)

- [x] Finalize `TicketContext`, `GapItem`, `TestScenario`, `TestPlanDocument` schemas in `llm.md`.
- [x] Define the **tool contracts** (name → input → stdout JSON) with exact field names.
- [x] Write the agent's **acceptance tests** before the agent exists:
  - [x] Happy path: fetch + normalize + gaps + draft + render, end to end.
  - [x] Sparse ticket: `KAN-1` has no AC → gaps section non-empty (18 rows), **no invented AC**.
  - [x] Bad key: `navigation.extract_jira_key` validates the pattern; an unparseable prompt stops
        before any HTTP call with a friendly message.
  - [x] Auth failure: a wrong token surfaces `HTTP 401` with a token-expiry hint and writes no plan.
  - [x] Not found: `HTTP 404` → "was not found (HTTP 404). Check the key and your access."
  - [x] Bad project: an unresolvable project key lists the projects the account can actually see.
- [x] Approve the blueprint (Phase 1 gate) → **unlocks Phase 2**.
- [x] Re-read the Protocol 0 Halt Rule and confirm all three conditions are met.

---

## 7. Phase 2 — Link checklist (complete — Jira Cloud v3)

- [x] Confirm env vars: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`.
- [x] Verify auth live: `tools/verify_connections.py` → `✓ jira Connected to Jira as …`.
- [x] Fetch real tickets (`KAN-1`, latest `KAN-5`) over the REST API and normalize them.
- [x] Discover the **acceptance-criteria field** via `GET /rest/api/3/field`
      (`jira_client.find_acceptance_criteria_field`); none configured, so the description/comment
      fallback was exercised instead.
- [x] Confirm ADF flattening: paragraphs, headings, bullet lists, inline cards, tables all survive
      (`KAN-1` description → 1,900 readable characters).
- [x] Confirm the v2 endpoints are gone (410) and the search path is `POST /rest/api/3/search/jql`.
- [x] Verify error handling surfaces structured, credential-free messages (400/401/403/404/410/429/5xx).
- [x] Confluence: out of scope per DQ-5.

---

## 8. Phase 3 — Architect checklist (complete — 3-layer A.N.T.)

- [x] **L3 Tools (deterministic):** `fetch_jira`, `fetch_comments`, `normalize_ticket`,
      `analyze_gaps`, `render_plan`, plus `verify_connections` and `run_agent` — pure, no LLM,
      JSON-in / JSON-out, callable as CLIs under `tools/`.
- [x] **L2 Navigation:** `core/navigation.py` orders the calls, enforces the review gate, records a
      step trace, and writes run artifacts.
- [x] **L1 Agent:** `core/agent.py` builds the grounded prompt and drafts the plan; scenarios are
      derived with explicit `AC-*`/`GAP-*` traceability.
- [x] Every layer boundary validates against the frozen schemas in `llm.md`.
- [x] Golden-file test: re-running `KAN-1` reproduces the same structure and gap list; only the
      model prose varies. The `.json` artifact makes this diffable.
- [x] Layer-1 SOPs written for every deterministic tool (`architecture/`).

---

## 9. Phase 4 — Stylize checklist (complete)

- [x] Plan rendering follows the canonical template section-for-section, with the mandatory
      `Test Scenarios (P0/P1/P2)` and `Gaps Summary` sections spliced in after Test Strategy.
- [x] "Gaps & Questions for the author" is always present and prominent (deterministic table).
- [x] Scenario IDs and `traces_to` render as a traceability table.
- [x] Clear banner: `STATUS: DRAFT — awaiting human review`, plus a Human Review Gate section.
- [x] Redaction: tokens never appear in artifacts, logs, or the UI; author display names are dropped.
- [x] UI polish: two-page Flask UI, rounded cards, responsive layout, no page-level horizontal
      scroll (wide tables scroll inside their own containers), inline connection-test feedback.

---

## 10. Phase 5 — Trigger checklist (not started)

- [ ] Define trigger: manual key, scheduled JQL poll, or webhook.
- [x] Self-healing (already in place): retry with backoff on 429/5xx, bounded attempts,
      surfaced after exhaustion.
- [ ] Monitoring: log every run (`key`, duration, tool calls, gap count, errors).
- [ ] Alert on repeated auth failures (token expiry).

---

## 11. Open Risks / Watch Items

- ADF descriptions may hide AC inside nested tables → flattening is table-aware and verified on a
  real ticket, but a ticket whose AC lives in a *comment table* has not been exercised yet.
- Acceptance criteria in comments can be edited after fetch → `fetched_at` is recorded in the artifact.
- Jira Cloud search endpoint churn (`/search` vs `/search/jql`) → the v3 POST form is pinned and the
  410 case has an explicit error message.
- Over-generation of scenarios dilutes signal → the prompt caps at 8-14 and requires traceability
  plus priority tags; observed output was 8 scenarios, all traceable.
- A 4B local model may ignore formatting instructions → the deterministic sections (gaps table,
  review gate, banner) are generated outside the model so the non-negotiable parts cannot drift.

---

## 12. Immediate Next Actions

1. ~~Answer Discovery Questions DQ-1 … DQ-9~~ — done, see §5.
2. ~~Freeze schemas in `llm.md` and remove the PROVISIONAL banner~~ — done.
3. ~~Get Blueprint approved → leave Protocol 0 halt and start Phase 2 (Link)~~ — done.
4. ~~Phases 1-4 implementation and local run~~ — done (see `progress.md`).

**Remaining (Phase 5 — Trigger), in priority order:**

1. Add per-run structured logging (`key`, duration, tool calls, gap count, errors) and a run index.
2. Schedule a JQL poll (e.g. tickets labelled `test-plan`) so plans are drafted on label change.
3. Alert on repeated auth failures so an expiring token is caught before a demo.
4. Optional: deliver the rendered plan to Confluence or Slack (DQ-8 left this open).
5. Optional: exercise the AC-in-comment-table path with a ticket that has one.
