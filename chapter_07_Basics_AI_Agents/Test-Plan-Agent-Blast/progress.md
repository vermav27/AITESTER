# progress.md — Run Log

> Protocol 0 artifact. Chronological log of what was done, errors hit, results seen.
> Cadence: an entry whenever work happens (target every 10–30 min during active sessions).
>
> Format: `## <timestamp> — <short title>` then **Done / Errors / Results / Next**.
> Times are local session time (IST). Append-only — never rewrite history.

---

## 2026-09-22 00:43 IST — Session start: Protocol 0 kickoff

**Done**
- Read `BLAST.md`; extracted Protocol 0 requirements (create project memory + constitution, then halt).
- Read `PromptUsed.md`; confirmed objective: **test plan creator from a Jira ID**.
- Confirmed the target folder holds only `BLAST.md` and `PromptUsed.md` (empty project otherwise).
- Activated the `testplan-create` skill and read its bundled resources:
  `fetch_jira.sh`, `requirement-checklist.md`, `Test_Plan_Template.md`, `vwo_details.md`.

**Errors**
- None.

**Results**
- Clear 4-file deliverable identified: `task_plan.md`, `findings.md`, `progress.md`, `llm.md`.
- Confirmed a working Jira REST fetcher already exists in the skill → reusable as the first L3 tool.
- Domain hint: Jira project likely **VWO**.

**Next**
- Author the four Protocol 0 files in this folder.
- Open Discovery Questions DQ-1 … DQ-9 for the project owner.

---

## 2026-09-22 00:52 IST — Authored Protocol 0 artifacts

**Done**
- Wrote `task_plan.md` — mission, DoD, B.L.A.S.T. phase map, Discovery Questions, per-phase checklists.
- Wrote `findings.md` — Jira field inventory, auth modes, 9 concrete `curl` request examples,
  error-code handling, data-shape findings, constraints, assumptions.
- Wrote `llm.md` — Project Constitution: 4 JSON schemas, behavioral rules R1–R12,
  architectural invariants I1–I7, end-to-end flow, tool contracts.
- Wrote this `progress.md` to establish the logging convention.

**Errors**
- None.

**Results**
- All four Protocol 0 files now exist under `Test-Plan-Agent-Blast/`.
- Schemas are marked **PROVISIONAL** pending the Phase 1 approval gate.

**Next**
- Get Discovery Questions answered.
- Freeze schemas (remove PROVISIONAL banner) and obtain Blueprint approval.
- Only then leave the Protocol 0 halt and begin Phase 2 (Link).

---

## 2026-09-22 00:55 IST — Protocol 0 verification

**Done**
- Re-listed the folder to confirm all four files are present and non-empty.
- Cross-checked internal consistency: filenames, schema names, and rule IDs line up
  across `task_plan.md`, `findings.md`, and `llm.md`.

**Errors**
- None.

**Results**
- Protocol 0 deliverable complete. Project is correctly parked at the **Halt Rule**
  (no `tools/` scripts written — by design).

**Next**
- Await answers to DQ-1 … DQ-9 and Blueprint sign-off before any tool code.

---

## 2026-09-22 01:05 IST — Blueprint approved implicitly; Phases 1-4 authorized

**Done**
- Owner instructed: "let's do the phase 1, phase 2, phase 3, phase 4, everything in one go" and
  "complete the project and run the project locally now" — the explicit Phase 1 approval.
- Resolved the blocking Discovery Questions from the answers in that instruction (see §5 of
  `task_plan.md` for the answered table).
- Decided the stack: **Flask** (not Streamlit, unlike chapter 3), keeping the 3-layer A.N.T. split
  from `llm.md` so the deterministic engine is reusable by both the web UI and CLI tools.

**Errors**
- None.

**Results**
- Halt Rule lifted: `tools/` code may now be written.
- New decision recorded: the deterministic engine lives in `core/` (importable), the Flask app in
  `app/` (presentation only), and `tools/` holds thin CLIs over `core/`.

**Next**
- Implement the L3 tools, L1 agent, L2 navigation, Flask app, and UI.

---

## 2026-09-22 01:21 IST — Core engine (L3 + L1 + L2) implemented

**Done**
- `core/config_manager.py` — `.env` load/save + secret masking.
- `core/jira_client.py` — REST v3 read-only client (issue, comments, myself, field discovery,
  project search, bounded `POST /search/jql`), bounded retry on 429/5xx, structured errors.
- `core/normalize.py` — ADF flattener (lists, tables, quotes, code) + AC discovery with source tags.
- `core/checklist.py` — deterministic 21-item gap analysis + ambiguity detection.
- `core/ollama_client.py` — `/api/tags` + `/api/chat` transport with bounded options.
- `core/agent.py` — pinned prompt assembly; section outline extracted from the canonical template.
- `core/render.py` — `TestPlanDocument` assembly, Markdown + JSON artifact writing.
- `core/navigation.py` — L2 orchestrator with a step trace and review-gate enforcement.

**Errors**
- None at write time. (Two defects found later by testing — see 01:26 and 01:29.)

**Results**
- `python -m compileall core app tools run.py` → clean.
- `python tools/verify_connections.py` → **✓ jira** (authenticated) and **✓ ollama** (`gemma3:4b`).
  Phase 2 (Link) handshake passed against live services.

**Next**
- Build the Flask app + UI, then run the pipeline end to end.

---

## 2026-09-22 01:26 IST — Flask app built; first live end-to-end run

**Done**
- `run.py` entry point, `app/` factory + `main`/`settings` blueprints, Jinja templates
  (`base`, `index`, `settings`), CSS, and progressive-enhancement JS.
- Settings page with Jira (URL/email/token/AC field) + Ollama (URL/model) and both connection tests.
- Flattened ADF and counted AC for **KAN-1** — 0 AC, which is *correct*: the ticket has no
  acceptance-criteria heading. Nothing was invented (rule R1 holding as designed).
- Ran the full pipeline: `python tools/run_agent.py "create a test plan for KAN-1"`.

**Errors**
- `extract_project_key("...the latest ticket in the QA project")` returned `None`. Cause: the
  `([A-Z][A-Z0-9]{1,9})\s+project` pattern was missing `re.IGNORECASE`, so it never matched the
  uppercased text. **Fix:** added the flag and reordered the patterns.
- Loose project guesses would have produced a confusing empty JQL search. **Fix:** added
  `jira_client.list_projects()` and `navigation.resolve_project_key()` so a guess is validated
  against the account's real projects and a bad guess fails with the available list.

**Results**
- Full run succeeded in **76.9 s**: fetched KAN-1 (0 comments), 18 gaps (17 missing, 1 ambiguous),
  drafted **6,279 characters** with `gemma3:4b`, 8 scenarios, wrote
  `runs/KAN-1-test-plan-20260922-012619.md`.
- Every scenario traced to a real `GAP-*` id; artifact carried `STATUS: DRAFT — awaiting human review`.

**Next**
- Validate the HTTP/UI path and fix the model's section placement.

---

## 2026-09-22 01:29 IST — UI validated over HTTP; section placement fixed

**Done**
- Started the server with `APP_DEBUG=0 python run.py`; smoke-tested over HTTP.
- `GET /` → 200 (3,084 B); `GET /settings` → 200 (5,498 B) after adding
  `strict_slashes=False` to remove the 308 redirect on `/settings`.
- `POST /settings/test/ollama` → `{"ok": true, "message": "Ollama is running with model 'gemma3:4b'."}`
- `POST /settings/test/jira` → `{"ok": true, "message": "Connected to Jira as …"}`
- `POST /generate` with an empty prompt → 400 with a friendly flash (validation works).
- `POST /generate` with a real prompt → **200, 26,195 B, 54.6 s**, containing the DRAFT badge,
  stats, gaps table, rendered plan, download buttons, and 6 completed pipeline steps.

**Errors**
- The model placed the scenario table under "Test Execution" because the section outline was built
  purely from the canonical 15 template sections, which name no scenarios section. **Fix:** added
  `EXTRA_SECTIONS` in `core/agent.py` to splice `Test Scenarios (P0/P1/P2)` and `Gaps Summary`
  into the outline, and told the prompt these two are mandatory additions. Verified the new
  artifact places both directly after "6. Test Strategy".
- A raw-token leak check on the Settings HTML returned **0 occurrences** — masking holds.

**Results**
- Verified artifact structure: `# Test Plan — KAN-1`, `## Document Information`, the 15 canonical
  sections with `## Test Scenarios (P0/P1/P2)` and `## Gaps Summary` inserted, then the
  deterministic `## Gaps & Questions for the author` and `## Human Review Gate`.
- Live projects on this instance: **KAN**, **SAM1**. Latest in KAN → `KAN-5`.

**Next**
- Refresh `task_plan.md`, `findings.md`, and `llm.md` to reflect the delivered build.

---

## Template for future entries

```
## <YYYY-MM-DD HH:MM TZ> — <short title>

**Done**
- <what was attempted / completed>

**Errors**
- <exact error text, cause, workaround>   (write "None." if clean)

**Results**
- <measured/observed outcome — what changed in the project>

**Next**
- <the next concrete action>
```

### Standing log rules
- Append-only; never edit past entries.
- Every error gets its **exact** message + the fix, even if trivial.
- Log a "no-change" entry when a check found nothing, so silence is never ambiguous.
- Keep entries factual: what happened, not what we hope happened.
