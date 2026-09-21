# SOP 04 — Render the plan and stop at the review gate

**Layer:** L3 tool (`core/render.py`) + L1 agent (`core/agent.py`) + L2 (`core/navigation.py`)
**Contract:** produces `TestPlanDocument` (`llm.md` §3.4) and the Markdown artifact.

## Goal

Assemble the LLM's draft into the canonical document, append the deterministic sections, and
**stop**. The run always ends at a human review gate; the status is never `final`.

## Split of responsibility

| Part of the document | Produced by | Why |
|---|---|---|
| Metadata header, AC list with sources | `render` (deterministic) | facts from Jira, not prose |
| Plan body (scope, strategy, scenarios…) | `agent` (LLM) | reasoning work |
| **Gaps & Questions table** | `render` (deterministic) | must be authoritative and complete |
| Human Review Gate + footer | `render` (deterministic) | must never be forgotten |
| `status` field | hard-coded `"draft"` | rule R2 |

## Tool logic

1. `agent.build_messages` assembles the prompt: the pinned instruction preamble, the rendered
   `TicketContext`, the gap table, and the **section outline extracted from
   `templates/Test_Plan_Template.md`** (so the prompt and the template cannot drift apart).
2. `ollama_client.chat` calls `POST /api/chat` with `temperature 0.2`, `num_ctx 8192`,
   `num_predict 2048` — bounded so a local 4B model cannot ramble indefinitely.
3. A wrapping ```-fence, if the model added one, is stripped.
4. `render.build_document` assembles the `TestPlanDocument`.
5. `render.render_markdown` writes the final document: title, DRAFT banner, metadata table,
   AC list, model body, gaps table, review gate.
6. `render.write_artifacts` writes `<KEY>-test-plan-<timestamp>.md` **and** `.json` into `runs/`.

## Scenario requirements enforced in the prompt

- 8–14 scenarios as a table with `id | Title | Type | Priority | Traces to | Steps | Expected result`.
- `Traces to` must cite a real `AC-*` or `GAP-*` id (rule R3).
- `P0` only for scenarios tied to an AC or a genuinely blocking gap.
- When no acceptance criteria exist, the model must say so and must not cite an `AC-*` id.

## Edge cases

| Case | Behaviour |
|---|---|
| Ollama unreachable / model missing | loud, specific error; no partial plan is written |
| Model wraps output in a code fence | fence stripped |
| Model emits raw HTML | neutralised before rendering in the UI; Markdown stays the artifact of record |
| Model cites an id that does not exist | visible in the draft; the deterministic gaps table remains the source of truth |
| Very long ticket | bounded `num_ctx`; the run reports the characters drafted |

## Invariants

- The rendered artifact is version-controllable text (invariant I5).
- No credentials or PII appear in any artifact (rules R4, R5).
- The gate section is unconditional — there is no code path that produces a `final` plan.
