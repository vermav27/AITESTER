# SOP 03 — Requirement gap analysis

**Layer:** L3 tool (`core/checklist.py`, CLI `tools/analyze_gaps.py`)
**Checklist:** `templates/requirement-checklist.md`
**Contract:** produces `GapItem[]` (`llm.md` §3.2).

## Goal

Decide, deterministically, which checklist items the ticket does **not** state and which it
states ambiguously. This is the highest-value output of the whole project — a tester's
leverage is asking the question before the bug ships.

This step needs no LLM. It is pure, repeatable, and unit-testable.

## Tool logic

1. **Build the corpus:** summary + flattened description + acceptance-criteria text + comment
   text + labels + components.
2. **Presence checks.** For each checklist item, search the corpus for its evidence patterns.
   No match ⇒ one `GapItem` with `status = "missing"` and a targeted question for the author.
3. **The AC check comes first.** If `acceptance_criteria` is empty, emit the single most
   important gap (no testable acceptance criteria) before anything else.
4. **Ambiguity checks.** Scan for untestable language (`TBD`, `etc.`, `handle gracefully`,
   `as appropriate`, `properly`, `user-friendly`, …). Each distinct marker ⇒ one `GapItem`
   with `status = "ambiguous"`, the matched snippet as evidence, and a question.
5. **Assign ids** `GAP-001…GAP-n` in emission order.

## Categories

`Functional` · `Data` · `NonFunctional` · `CrossCutting` · `Clarity` — matching the checklist file.

## Edge cases

| Case | Behaviour |
|---|---|
| Very sparse ticket | many gaps — correct, and surfaced prominently |
| Excellent ticket | zero gaps ⇒ "every checklist item has evidence" |
| Marker appears in unrelated prose | still reported as `ambiguous`; the evidence snippet lets a human judge |
| Duplicate marker | reported once, not once per occurrence |
| Same checklist item as a gap and an ambiguity | allowed: they answer different questions |

## Invariants

- Deterministic: same ticket ⇒ same gap list, every run (rule R8).
- Evidence is always quoted from the ticket; no invented content.
- Gaps never block the draft — they *become* the draft's open questions and the review gate's
  checklist (rule R2).
