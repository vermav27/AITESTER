# Test Plan Agent (Flask)

A local-first Flask application that turns a **Jira ticket into a review-ready test plan**.

You type a plain-English request — *"fetch this Jira and create a test plan for KAN-1"* — and the
agent fetches the ticket over the Jira REST API, scores it against a requirement checklist,
drafts a full test plan with your **locally installed Ollama model**, and **stops at a human
review gate**. No cloud LLM is involved.

This is Phase 1-4 of the `BLAST.md` protocol (Blueprint → Link → Architect → Stylize) built on the
A.N.T. three-layer architecture defined in `llm.md`.

---

## What it does

| Step | Layer | What happens |
|---|---|---|
| 1. Resolve | L2 | Reads the prompt, extracts the issue key (or resolves the latest ticket in a named project) |
| 2. Fetch | L3 | `GET /rest/api/3/issue/{KEY}` + `/comment`, read-only, retried on 429/5xx |
| 3. Normalize | L3 | Flattens Atlassian Document Format, finds acceptance criteria and records their source |
| 4. Analyze | L3 | Runs the requirement checklist → `GapItem[]` (missing / ambiguous) |
| 5. Draft | L1 | Prompt built from the ticket + gaps + canonical section outline → Ollama `/api/chat` |
| 6. Render | L3 | Assembles the document: DRAFT banner, metadata, authoritative gaps table, review gate |
| 7. Gate | L2 | Writes `runs/<KEY>-test-plan-<timestamp>.{md,json}` and **stops**. Status is always `draft` |

## What it deliberately does not do

- **Never invents acceptance criteria.** A missing AC is a *finding* (a `GAP-*` row), never a blank
  that gets filled in.
- **Never mutates Jira.** The client issues reads only.
- **Never declares a plan final.** There is no code path that emits `status: final`.
- **Never leaks secrets or PII.** Tokens never appear in artifacts, logs, or the UI; reporter/author
  names are dropped during normalization.
- **Never treats LLM output as gospel.** The gaps table and the review gate are generated
  deterministically, not by the model.

---

## Architecture

```
                    ┌──────────────────────────────────────────────┐
  prompt ──────────►│  L2 Navigation  core/navigation.py           │
                    │  resolve → fetch → normalize → analyze →     │
                    │  draft → render → GATE → stop                │
                    └───────┬───────────────────────────┬──────────┘
                            │ calls L3                  │ calls L1
        ┌───────────────────▼──────────────────┐  ┌─────▼───────────────────┐
        │ L3 Tools (deterministic)             │  │ L1 Agent (reasoning)    │
        │ jira_client · normalize · checklist  │  │ agent.py → prompt +     │
        │ render · ollama_client · config      │  │ plan draft via Ollama   │
        └──────────────────────────────────────┘  └─────────────────────────┘
                            ▲
                    ┌───────┴──────────────────────────────────────────┐
                    │ Flask presentation  app/ (factory + blueprints)  │
                    │ GET /  POST /generate  GET /settings  POST …/test│
                    └──────────────────────────────────────────────────┘
```

The Flask layer only renders HTML and delegates. The deterministic/LLM boundary is enforced by the
`TicketContext`, `GapItem`, `TestScenario`, and `TestPlanDocument` JSON schemas in `llm.md`.

---

## Folder structure

```text
Test-Plan-Agent-Blast/
├── README.md                       # this file
├── BLAST.md                        # the governing protocol
├── PromptUsed.md                   # build prompt
├── task_plan.md                    # phases, goals, checklists
├── findings.md                     # research: Jira fields, endpoints, auth, errors
├── progress.md                     # append-only run log
├── llm.md                          # project constitution: schemas, rules, invariants
├── run.py                          # entry point — python run.py
├── requirements.txt
├── .env                            # real config (gitignored)
├── .env.example                    # placeholder template
├── .gitignore
├── app/                            # Flask presentation layer
│   ├── __init__.py                 # create_app() factory, markdown filter
│   ├── routes/
│   │   ├── main.py                 # GET /  ·  POST /generate  ·  GET /runs/<file>
│   │   └── settings.py             # GET/POST /settings  ·  POST /settings/test/{jira,ollama}
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html              # prompt UI + result
│   │   └── settings.html           # Jira / Ollama config + connection tests
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── core/                           # the engine
│   ├── config_manager.py           # L3 — .env load/save/mask
│   ├── jira_client.py              # L3 — Jira REST v3 (read-only)
│   ├── normalize.py                # L3 — raw issue → TicketContext
│   ├── checklist.py                # L3 — deterministic gap analysis
│   ├── render.py                   # L3 — TestPlanDocument → Markdown + JSON
│   ├── ollama_client.py            # L3 — Ollama transport
│   ├── agent.py                    # L1 — prompt assembly + drafting
│   └── navigation.py               # L2 — orchestrator + review gate
├── tools/                          # B.L.A.S.T. Phase 3 L3 CLIs
│   ├── fetch_jira.py
│   ├── fetch_comments.py
│   ├── normalize_ticket.py
│   ├── analyze_gaps.py
│   ├── render_plan.py
│   ├── verify_connections.py       # Phase 2 Link handshake
│   └── run_agent.py                # whole pipeline from the CLI
├── architecture/                   # B.L.A.S.T. Phase 3 Layer 1 SOPs
│   ├── 01_fetch_jira_SOP.md
│   ├── 02_normalize_ticket_SOP.md
│   ├── 03_gap_analysis_SOP.md
│   └── 04_render_and_review_gate_SOP.md
├── prompts/
│   └── test_plan_prompt.md         # the pinned drafting prompt
├── templates/                      # canonical, fixed output shape
│   ├── Test_Plan_Template.md
│   └── requirement-checklist.md
├── runs/                           # generated plans (.md + .json)
├── .tmp/                           # scratch space for intermediate files
└── venv/                           # local virtualenv (gitignored)
```

---

## Quick start

```bash
cd chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast

python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # then fill in your real values
python run.py
```

Open **http://127.0.0.1:5000**.

Confirm both services are reachable before generating:

```bash
python tools/verify_connections.py
```

Expected:

```text
  ✓ jira    Connected to Jira as <you>.
  ✓ ollama  Ollama is running with model 'gemma3:4b'.

Link verified — both services are reachable.
```

### Prerequisites

- Python 3.9+
- Ollama running locally with a model pulled (`ollama pull gemma3:4b`)
- A Jira Cloud account and an API token (Atlassian → Account settings → Security → API tokens)

---

## Configuration

Configuration lives in the gitignored `.env` file and can be edited from the **Settings** page.
`.env` is authoritative; a shell environment variable is used only when the file has no value.

| Variable | Purpose |
|---|---|
| `JIRA_BASE_URL` | Jira site, e.g. `https://your-domain.atlassian.net` |
| `JIRA_EMAIL` | Jira account email (present ⇒ HTTP Basic auth) |
| `JIRA_TOKEN` | Jira API token. Leave `JIRA_EMAIL` blank to send it as a Bearer token instead |
| `JIRA_AC_FIELD_ID` | *Optional.* Custom field holding acceptance criteria, e.g. `customfield_10001` |
| `OLLAMA_BASE_URL` | Usually `http://localhost:11434` |
| `OLLAMA_MODEL` | Installed model tag, e.g. `gemma3:4b` |
| `APP_HOST` / `APP_PORT` | Optional Flask bind override (default `127.0.0.1:5000`) |
| `APP_DEBUG` | `1` (default) enables the Flask debugger and auto-reload |

Find the acceptance-criteria field id for your instance:

```bash
python -c "from core import config_manager, jira_client; print(jira_client.find_acceptance_criteria_field(config_manager.load_config()))"
```

### Settings page

- **Jira:** Base URL, Email ID, API token, optional acceptance-criteria field.
- **Ollama:** Base URL and model (a datalist shows what is installed locally).
- **Test Jira connection** → `GET /rest/api/3/myself`.
- **Test Ollama connection** → `GET /api/tags`, and confirms the configured model is installed.
- Secrets are masked (`ATATT3…BE68`) and a blank secret field keeps the stored value.

---

## Using the app

### Generate

1. Type a request. Any of these work:
   - `Fetch this Jira and create a test plan for KAN-1` — explicit key
   - `Write a test plan for KAN-5`
   - `Create a test plan for the latest ticket in KAN` — no key, resolves the newest ticket
2. Click **Generate test plan**. A local 4B model typically takes 60-120 s.
3. Review the result: pipeline trace, summary stats, the gaps table, the rendered plan, and the
   human review gate.
4. **Download Markdown** or **Download JSON**, or copy the plan to the clipboard.

A request naming a project that does not exist fails loudly and lists the projects your account
can actually see.

### Output artifacts

Every run writes two files into `runs/`:

| File | Contents |
|---|---|
| `<KEY>-test-plan-<timestamp>.md` | The review-ready document: DRAFT banner, metadata, AC list with sources, drafted sections, authoritative gaps table, Human Review Gate |
| `<KEY>-test-plan-<timestamp>.json` | The machine-readable `TestPlanDocument` (same data, for diffing/re-runs) |

Re-running the same key produces the same *structure*; only the model's prose varies (rule R8).

---

## Command-line tools

The same deterministic engine, without the browser:

```bash
# Phase 2 Link handshake
python tools/verify_connections.py

# Fetch raw pieces
python tools/fetch_jira.py KAN-1
python tools/fetch_comments.py KAN-1

# Normalize and inspect acceptance criteria
python tools/normalize_ticket.py KAN-1
python tools/normalize_ticket.py --from-stdin < issue.json

# Gap analysis only — fast, no LLM
python tools/analyze_gaps.py KAN-1

# Whole pipeline
python tools/run_agent.py "create a test plan for KAN-1"
python tools/run_agent.py "latest ticket in KAN" --markdown-only

# Render a document you assembled yourself
python tools/render_plan.py --key KAN-1 --draft my-draft.md
python tools/render_plan.py --document runs/KAN-1-test-plan-….json
```

There is also an HTTP endpoint layer for the app: `POST /generate`,
`POST /settings/test/jira`, `POST /settings/test/ollama`, `GET /runs/<file>`.

---

## How the two halves of the output are produced

| Section of the final document | Produced by | Why |
|---|---|---|
| Metadata header, AC list with sources | `core/render.py` — deterministic | facts from Jira |
| Plan body (objective, scope, strategy, scenarios…) | `core/agent.py` — LLM | reasoning work |
| **Gaps & Questions for the author** | `core/checklist.py` + `render` — deterministic | must be complete and authoritative |
| Human Review Gate | `core/render.py` — deterministic | must never be omitted |
| `status: draft` | hard-coded | rule R2 |

The section headings are extracted from `templates/Test_Plan_Template.md` at prompt-build time, so
the prompt and the fixed template cannot drift apart. `Test Scenarios (P0/P1/P2)` and
`Gaps Summary` are spliced in as mandatory additions.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Jira authentication failed (HTTP 401)` | The token is wrong or expired — generate a new one and update the Settings page. |
| `Project 'X' was not found or is not accessible` | The message lists the projects your account can see; use one of those keys. |
| `HTTP 410` from Jira | A legacy REST v2 endpoint is being called. This app targets API v3 only. |
| `Unable to reach Ollama` | Start it: `ollama serve`, then re-test. |
| `model '…' is not installed` | Run `ollama list` and set `OLLAMA_MODEL` to an exact tag shown there. |
| Generation is slow | Expected on CPU with a 4B model. Try a smaller ticket or `gemma3:1b`. |
| Settings appear not to save | Confirm the project directory is writable — settings are written to `.env`. |
| `No Jira issue key found in your request` | Include a key (`KAN-1`) or name a project (`latest ticket in KAN`). |

---

## Validation checklist

- [x] `python run.py` serves both pages; `/` and `/settings` return 200.
- [x] `tools/verify_connections.py` passes for Jira and Ollama.
- [x] A real ticket is fetched over REST v3 and normalized into `TicketContext`.
- [x] Acceptance criteria are extracted only when present, with the source recorded.
- [x] A ticket without acceptance criteria produces a `GAP` and **no** invented AC.
- [x] Gap analysis is deterministic and needs no LLM.
- [x] The full pipeline drafts a plan with `gemma3:4b` and writes `.md` + `.json` artifacts.
- [x] Every scenario traces to an `AC-*` or `GAP-*` id.
- [x] The artifact always carries `STATUS: DRAFT — awaiting human review`.
- [x] The raw API token never appears in the UI HTML, a log line, or an artifact.
- [x] A bad key, a bad project, and an empty prompt all fail loudly with actionable messages.

---

## Security notes

- Credentials are read from the gitignored `.env` only — never hardcoded, never committed.
- Secrets are masked in the UI, never logged, and never written into a generated plan.
- Jira access is read-only: no transitions, comments, or edits.
- The agent is intended for `127.0.0.1` only. Flask's dev server is not hardened for public
  exposure, and it has no authentication of its own.
- Ticket text and model output are untrusted: raw HTML is neutralized before it reaches the
  browser, and `javascript:`/`data:` URLs are stripped from links.
- Rotate the Jira API token if it has ever been exposed or pasted somewhere unsafe.
