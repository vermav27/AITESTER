# SOP 02 — Normalize a ticket

**Layer:** L3 tool (`core/normalize.py`, CLI `tools/normalize_ticket.py`)
**Contract:** produces `TicketContext` (`llm.md` §3.1).

## Goal

Turn a deeply nested Jira payload into the flat, testable `TicketContext` the rest of
the pipeline depends on — and record *where* each acceptance criterion was found.

## Inputs / output

| | Shape |
|---|---|
| In | raw issue JSON + comments JSON + config |
| Out | `TicketContext` JSON on stdout |

## Tool logic

1. **Flatten ADF.** Walk the Atlassian Document Format tree and render Markdown-ish text.
   Paragraphs, headings, bullet/ordered lists, code blocks, quotes, and **tables** are all
   preserved — criteria frequently live in a table or bullet list and must survive flattening.
2. **Discover acceptance criteria, in strict precedence order:**
   1. the configured custom field `JIRA_AC_FIELD_ID`, if set and non-empty;
   2. otherwise a section in the description introduced by a recognised heading
      (`Acceptance Criteria`, `Acceptance Test`, `Done When`, `Definition of Done`, `AC:`);
   3. otherwise a comment containing such a heading.
3. **Tag the source** of each criterion (`field` / `description` / `comment`) so the tester
   knows how much to trust it.
4. **De-duplicate** on a punctuation-insensitive signature, then assign `AC-1…AC-n` in order.

## Edge cases

| Case | Behaviour |
|---|---|
| No criteria anywhere | `acceptance_criteria: []` — **never** inferred or back-filled from prose |
| A table of criteria | captured cell-by-cell; header rows and index columns dropped |
| A wiki-markup (`h3.`) heading | also recognised |
| Description is plain text, not ADF | treated as text and parsed the same way |
| Comment authored by someone | author display name is **not** emitted (rule R5, no PII) |
| AC heading followed by unrelated headings | capture stops at the next recognised heading |

## Invariants

- A missing acceptance criterion is a *finding*, not a blank to fill (rule R1).
- `source` is always recorded (rule R11).
- Only fields present in the ticket are emitted; nothing is defaulted into existence.
