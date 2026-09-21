# findings.md — Research, Discoveries, Constraints

> Protocol 0 artifact. Everything we learned while researching *how to turn a Jira ID
> into a test plan*: what data exists in Jira, how to fetch it reliably, what the
> skill/repo already gives us, and the constraints we must design around.
>
> Requests below are **read-only**. The agent never writes to Jira.

---

## 0. Source material we started from

| Source | What it gives us |
|---|---|
| `BLAST.md` | Protocol 0 requirements + the B.L.A.S.T. phase model and Halt Rule. |
| `.agents/skills/testplan-create/SKILL.md` | The 4-step workflow: fetch → gap-analyze → draft → STOP for review. |
| `…/scripts/fetch_jira.sh` | Working `curl + jq` Jira fetcher (the L3 tool seed). |
| `…/references/requirement-checklist.md` | The gap-analysis checklist (Functional / Data / Non-functional / Cross-cutting / Clarity). |
| `…/references/template/Test_Plan_Template.md` | Canonical output template (15 sections + appendices). |
| `…/assets/vwo_details.md` | Domain context — Jira project appears to be **VWO**. |

### Key workflows discovered (from the skill)
1. **Fetch** the ticket (MCP preferred → script fallback → ask user to paste; *never invent*).
2. **Analyze & find missing pieces** against the requirement checklist → "Gaps & Questions".
3. **Draft** the test plan from the template, derive scenarios from AC + gaps, tag P0/P1/P2.
4. **STOP for human review** — mandatory gate; never mark "final".

---

## 1. What fields we need out of Jira (and why)

| Field | Used for | Notes |
|---|---|---|
| `key` | filename, traceability | Primary handle, e.g. `VWO-123`. |
| `summary` | plan title | One line. |
| `issuetype` | context (Story/Bug/Task) | Shapes scenario style. |
| `status` | context | Sprint board state. |
| `priority` | risk weighting | Informs P0/P1/P2. |
| `description` | **primary AC source?** | Atlassian Document Format (ADF) → must flatten. |
| `components` | scope / module labels | Drives Environment & Scope. |
| `labels` | filtering / tagging | Often carries `test-plan`, squad tags. |
| `fixVersions` | Release field | Template "Version / Release". |
| `issuelinks` | linked stories/specs/bugs | Expands scope + Confluence links. |
| `attachment` | mockups/logs | Evidence references. |
| `comment` | **AC often lives here** | Must fetch separately. |
| custom field (AC) | structured acceptance criteria | Field id varies per instance → discover via `/field`. |

> **Finding:** acceptance criteria are *not* standardized in Jira. They may be a custom
> field, inside the description (often a table), or only in comments. The agent must
> try all three and report which source it used.

---

## 2. Authentication — how we get in

| Mode | Instance | Header | Env vars |
|---|---|---|---|
| **Basic (email + API token)** | Atlassian **Cloud** | `-u "$JIRA_EMAIL:$JIRA_TOKEN"` | `JIRA_EMAIL`, `JIRA_TOKEN` |
| **Bearer (PAT)** | **Server / Data Center** | `-H "Authorization: Bearer $JIRA_TOKEN"` | `JIRA_TOKEN` |

Both require `JIRA_BASE_URL`, e.g. `https://yourco.atlassian.net`.

**Constraint:** secrets come **only** from environment variables — never written to
files, logs, or the produced plan. (Matches the `llm.md` rule R4.)

> **Finding:** there is (currently) no Jira MCP server wired into this workspace, so the
> **REST fallback is the primary path** until DQ-4 is answered.

---

## 3. Requests we will use (curl)

### 3.1 Fetch one issue (Cloud, Basic auth) — the core call
```bash
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" \
  -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${KEY}?fields=summary,description,issuetype,priority,status,components,labels,fixVersions,issuelinks,attachment,comment"
```

### 3.2 Same, with a custom Acceptance-Criteria field
```bash
# First discover the field id:
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/field" | jq '.[] | select(.name|test("acceptance";"i")) | {id,name}'

# Then request it (id looks like customfield_10xxx):
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${KEY}?fields=summary,description,customfield_10000"
```

### 3.3 Server / Data Center (Bearer PAT)
```bash
curl -sS -H "Authorization: Bearer ${JIRA_TOKEN}" \
  -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/2/issue/${KEY}?fields=summary,description,comment"
```
> Server/DC typically uses REST **v2**; API v3 (with ADF) is Cloud.

### 3.4 Fetch comments (AC often hides here)
```bash
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${KEY}/comment?maxResults=100&orderBy=created"
```

### 3.5 Fetch links field only (cheap scope expansion)
```bash
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${KEY}?fields=issuelinks" \
| jq '.fields.issuelinks[] | {type: .type.name, key: (.outwardIssue.key // .inwardIssue.key)}'
```

### 3.6 "Latest ticket in project" — JQL search
```bash
# Cloud: the old GET /search is deprecated → use POST /search/jql
curl -sS -X POST -u "${JIRA_EMAIL}:${JIRA_TOKEN}" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/search/jql" \
  -d '{"jql":"project = VWO ORDER BY created DESC","maxResults":1,"fields":["summary","issuetype","status"]}'
```
> Fallback for older instances: `GET /rest/api/3/search?jql=...&maxResults=1`.

### 3.7 Download an attachment (only if a ticket needs it)
```bash
curl -sSL -u "${JIRA_EMAIL}:${JIRA_TOKEN}" \
  -o "attachment.bin" \
  "${JIRA_BASE_URL}/rest/api/3/attachment/content/${ATTACHMENT_ID}"
```

### 3.8 Linked Confluence page (if DQ-5 = yes)
```bash
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${CONFLUENCE_BASE_URL}/wiki/rest/api/content/${PAGE_ID}?expand=body.storage,version"
```

### 3.9 Suggested normalizer (deterministic, L3)
```bash
curl -sS -u "${JIRA_EMAIL}:${JIRA_TOKEN}" -H "Accept: application/json" \
  "${JIRA_BASE_URL}/rest/api/3/issue/${KEY}?fields=summary,description,issuetype,priority,status,components,labels,fixVersions,issuelinks,attachment,comment" \
| jq '{
    key: .key,
    summary: .fields.summary,
    type: .fields.issuetype.name,
    status: .fields.status.name,
    priority: .fields.priority.name,
    components: [.fields.components[]?.name],
    labels: .fields.labels,
    fixVersions: [.fields.fixVersions[]?.name],
    description: .fields.description,
    links: [.fields.issuelinks[]? | {type: .type.name, key: (.outwardIssue.key // .inwardIssue.key)}],
    attachments: [.fields.attachment[]? | .filename],
    comments: [.fields.comment.comments[]? | {author: .author.displayName, body: .body}]
  }'
```

---

## 4. Error handling — what we must surface (fail loud)

| HTTP | Meaning | Agent behavior |
|---|---|---|
| `400` | Bad JQL / bad fields | Show the request, stop. |
| `401` | Bad/expired token | Loud auth error; hint at token expiry. Do **not** emit a plan. |
| `403` | No permission to the project/issue | Loud error with the key. |
| `404` | Key not found / no access | "Ticket not found", exit non-zero. |
| `429` | Rate limited | Back off + retry (bounded); respect `Retry-After`. |
| `5xx` | Jira incident | Retry with backoff, then surface. |

> **Invariant:** a failed fetch must never degrade into an empty or hallucinated plan.

---

## 5. Data shape findings

- **ADF:** Cloud `description` is Atlassian Document Format (nested JSON), not text.
  Needs flattening; AC frequently lives inside ADF **tables** and **bullet lists**.
- **Comments** are also ADF on v3 (`body` is a doc node).
- **Custom fields:** acceptance-criteria field id differs per instance → discover, never hardcode.
- **Pagination:** comments/attachments may paginate (`maxResults`, `startAt`/`nextPageToken`).
- **Timestamps:** track `fetched_at` — tickets change between runs (AC edits in comments).

---

## 6. Constraints (must design around)

1. **Read-only.** Never transition, comment on, or mutate a Jira issue.
2. **No credentials/PII** in any artifact (rule R4/R5).
3. **No fabrication** — missing AC is a *finding*, not a blank to fill (rule R1).
4. **Always end at a review gate** — status `draft`/`in_review`, never `final` (rule R2).
5. **Traceability** — every P0 scenario maps to an AC or a GAP (rule R3).
6. **Determinism** — fetching/normalizing/rendering live in `tools/`, not in the LLM.
7. **Halt Rule** — no `tools/` scripts until Discovery Questions + schema + blueprint are done.

---

## 7. Assumptions to confirm

- **A1:** Jira Cloud + Basic auth is the default target (pending DQ-1).
- **A2:** The in-scope project is `VWO` (from `vwo_details.md`; pending DQ-2).
- **A3:** "A.N.T. 3-layer architecture" = **A**gent / **N**avigation / **T**ools
  (used as our working definition; confirm intent in the Blueprint).
- **A4:** Output is a Markdown file based on the bundled Test Plan Template (pending DQ-6).
- **A5:** Confluence is optional for v1 (pending DQ-5).

---

## 8. Resolved during Phases 1-4

- [x] Confirm DQ-1 … DQ-9 — all answered; see `task_plan.md` §5.
- [x] Discover the real AC field id on the target instance — **none configured**
      (`find_acceptance_criteria_field` returned no match), so the description → comment fallback
      is the live path. `KAN-1` genuinely has no acceptance-criteria heading.
- [x] Validate ADF flattening on a real ticket — `KAN-1` (headings, paragraphs, a bullet list, an
      inline card) flattened to 1,900 readable characters. A *table* flattener is implemented and
      table rows render as pipe rows, but no ticket with an AC **table** has been exercised yet.
- [x] Choose and pin the search endpoint — `POST /rest/api/3/search/jql` with a bounded
      `maxResults`; the legacy `GET /search` is gone (410) on this instance.
- [x] Confirm where generated plans should be delivered — local `runs/<KEY>-test-plan-<ts>.md`
      plus a matching `.json`, downloadable from the UI. Confluence/Slack delivery deferred to Phase 5.

**Verified live (2026-09-22):** Jira projects visible to this account are **`KAN`** and **`SAM1`**;
the latest ticket in `KAN` is **`KAN-5`**.

---

## 9. Endpoint facts confirmed against the live instance

| Request | Result |
|---|---|
| `GET /rest/api/3/myself` | 200 — auth works with email + API token (Basic) |
| `GET /rest/api/3/issue/KAN-1?fields=…` | 200 — `description` is ADF; `components` empty; `labels: ["High"]` |
| `GET /rest/api/3/issue/KAN-1/comment` | 200 — zero comments |
| `GET /rest/api/3/project/search?maxResults=100` | 200 — `values[]` → `KAN`, `SAM1` |
| `POST /rest/api/3/search/jql` | 200 — resolves the latest issue in a project |
| REST **v2** family | **410 Gone** — never use it on this instance |

**Field reality check:** `issuetype`, `priority`, `status`, `labels`, `fixVersions`, `components`,
`issuelinks`, and `attachment` all resolve as documented. `comments` come back as a *separate*
request, not as a populated `fields.comment` on the issue request.

---

## 10. Findings from the live pipeline run

| Observation | Detail |
|---|---|
| First end-to-end run | `KAN-1` in **76.9 s** with `gemma3:4b` on CPU; 6,279 characters drafted |
| Second run (via HTTP) | **54.6 s**, 26,195-byte rendered page |
| Gap output on `KAN-1` | **18 gaps** — 17 missing, 1 ambiguous (`user-friendly`) |
| Acceptance criteria | 0 found → the agent reported a `GAP-001` and invented nothing (rule R1 verified) |
| Scenarios | 8 drafted, every one tracing to a real `GAP-*` id; priorities varied P0/P1/P2 |
| Model instruction-following | The model **ignored** the section list on the first run and filed the scenario table under *Test Execution* → fixed by splicing explicit sections into the outline (see §11) |
| Model quality | Good at prose and scenario derivation; unreliable at strict structural instructions when they conflict. Hence the deterministic wrapper. |
| Latency envelope | A full plan on a 4B CPU model is 50-120 s. The UI shows a busy state and a longer-wait message; the Ollama client timeout is 300 s. |

---

## 11. Implementation defects found and fixed

1. **Project-key regex missing `re.IGNORECASE`.**
   `"…the latest ticket in the QA project"` resolved to `None` because the
   `([A-Z][A-Z0-9]{1,9})\s+project` pattern was compiled without the flag and the text is
   uppercased before matching. Fixed, and the patterns were reordered to try the
   `X project` form before the looser `in X` form.

2. **Loose project guesses could produce a confusing empty search.**
   An `in X` guess on ordinary prose ("…in Detail…") would build JQL for a non-existent project.
   Fixed by adding `jira_client.list_projects()` and `navigation.resolve_project_key()`, which
   validate the guess against the account's real projects and otherwise fail with the available
   list. Observed: `Project 'QA' was not found or is not accessible… Available projects: KAN, SAM1.`

3. **`config_manager` staleness (a latent bug inherited from the chapter-3 pattern).**
   Chapter 3 calls `load_dotenv(ENV_FILE, override=False)`, which mutates `os.environ`; a later
   `load_config()` then reads the *stale* environment value and the Settings page appears not to
   save. This project reads the `.env` file directly with `dotenv_values()` and never mutates
   `os.environ`, so `.env` is authoritative and edits take effect immediately.

4. **`/settings` returned 308.** Fixed with `strict_slashes=False` so both `/settings` and
   `/settings/` work without a redirect.

5. **Model filed scenarios under the wrong heading.** Fixed with `EXTRA_SECTIONS` in
   `core/agent.py` (see §13 below and `llm.md` §8).

6. **Two sections shared the name "Gaps & Questions for the author".** The prompt now asks the
   model for a `Gaps Summary`, leaving the authoritative table to the deterministic renderer.

---

## 12. Environment notes

| Item | Detail |
|---|---|
| Python | 3.9.6 (system) — the code uses `from __future__ import annotations` and `typing.Dict/List`, so no 3.10+ syntax |
| Dependencies | `Flask 3.1.3`, `requests 2.32.5`, `python-dotenv 1.2.1`, `Markdown 3.9` |
| Ollama | `gemma3:4b` (3.3 GB) and `gemma3:1b` (815 MB) installed; server on `:11434` |
| Warning | `NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently LibreSSL 2.8.3` — harmless on macOS system Python; requests still succeed |
| `.env` | Real credentials live here and the file is **gitignored**; `.env.example` holds placeholders only |

---

## 13. Design decisions worth remembering

- **Split gap analysis.** Deterministic code computes `GapItem[]`; the LLM only derives prose and
  scenarios. This makes rule R1 enforceable regardless of model behaviour, and makes the most
  valuable section of the output reproducible.
- **Markdown in, deterministic wrapper out.** A 4B model emits unreliable nested JSON but usable
  Markdown, so the contract is "model writes the body, code writes the frame".
- **Config precedence: file over environment.** `.env` wins so the in-app Settings page is the
  single control surface; a shell variable only fills a key the file omits.
- **`core/` is importable, `tools/` is thin.** The CLIs exist so the deterministic engine can be
  driven without a browser, not as a second implementation.
- **Untrusted input is neutralized at the boundary.** Raw HTML from tickets or model output is
  escaped before Markdown conversion; `javascript:`/`data:` URLs are stripped from links.

