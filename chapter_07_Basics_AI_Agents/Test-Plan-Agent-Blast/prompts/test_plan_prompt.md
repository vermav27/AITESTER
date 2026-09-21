You are drafting a test plan for Jira ticket `{{KEY}}` — {{TITLE}}.

Everything you may use is below. If a fact is not here, it does not exist:
do not invent acceptance criteria, requirements, environments, dates, or names.

# Jira ticket (already fetched and normalized — treat as the only source of truth)

{{TICKET_CONTEXT}}

# Requirement checklist findings (already computed deterministically)

Every row is something this ticket does **not** state, or states ambiguously.
Use these ids (`GAP-###`) when you reference a deficiency. Do not repeat the table
verbatim — it is appended to the final document automatically.

{{GAP_TABLE}}

# What to produce

Write the body of the test plan in GitHub-flavoured Markdown, using **exactly** these
sections, in this order, and nothing before the first heading:

{{SECTION_OUTLINE}}

`Test Scenarios` and `Gaps Summary` are mandatory additions to the standard template —
give them their own level-2 headings exactly as spelled above.

Rules for the content:

1. Keep it concise and useful. Aim for 2-6 bullets per section. Do not pad.
2. **Test Scenarios** is the most important section. Produce 8-14 scenarios as a table:

   | id | Title | Type | Priority | Traces to | Steps | Expected result |
   |---|---|---|---|---|---|---|
   | TS-001 | … | positive / negative / boundary / cross-role | P0 / P1 / P2 | AC-1, GAP-003 | 1) … 2) … | … |

   - Cover positive, negative, boundary, and cross-role/permission paths.
   - `Traces to` must reference at least one real `AC-*` or `GAP-*` id from above.
   - `P0` only for scenarios tied to an `AC-*` id or to a genuinely blocking gap.
   - If there are no acceptance criteria, say so in the Objective and derive scenarios
     from the description and the gaps — never cite an `AC-*` id that does not exist.
3. In **Gaps Summary**, write a short paragraph naming the 3-5 highest-risk missing items by
   id and what each one blocks. Do not write your own table and do not use the heading
   "Gaps & Questions for the author" — the authoritative gaps table is appended to the final
   document automatically.
4. Populate environments, data, and dates only as clearly-labelled placeholders such as
   `[QA environment — confirm]`. Never state a plausible-sounding fact as if it were known.
5. Do not include credentials, tokens, URLs with secrets, or any personal information.
6. Never call the plan final or approved. It is a draft for human review.
7. Output Markdown only: no code fences around the document, no commentary before or after.
