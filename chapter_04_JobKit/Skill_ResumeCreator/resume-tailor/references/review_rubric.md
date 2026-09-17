# Scored Resume Review Rubric

Use this when the user asks for a review, a score, or feedback on a resume. It's also the yardstick for fresh rebuilds: aim for 8 or higher in every category, and say plainly which scores depend on the user supplying real numbers.

## Output format (use exactly)

```
# Resume Review: <Name>, <Target Role>

## 1. Overall Result: **N/10**
<2–3 sentences: the verdict and the two biggest issues>

## 2. Effectivity: **N/10**
✅ ...
🙈 ...

## 3. Layout and Design: **N/10**
✅ ...
🙈 ...

## 4. Content Relevance: **N/10**
✅ ...
🙈 ...

## 5. Grammar and Syntax: **N/10**
✅ ...
🙈 ...

## 6. Impact: **N/10**
✅ ...
🙈 ...
<Current → Stronger rewrite table with [X] placeholders>

## 🎯 Top 5 Priority Fixes
1. ...
```

Use ✅ for strengths and 🙈 for areas to improve. Give 2–4 of each per category, each specific enough to act on and quoting or naming the exact spot in the resume. The overall score is a judgment, not an average; weight Impact and Content Relevance most.

## What each category checks

**Effectivity: does the resume prove the candidate can do the target job?**
- A clear career direction that matches the target role.
- Skills tied to named projects or clients, not just listed.
- Leadership or ownership shown with scope (team size, number of projects, releases), not merely claimed.
- The title history supports the positioning, with progression shown if it exists.
- The best experience gets the most space; no repeated claims.

**Layout and Design: can a human skim it and an ATS parse it?**
- One column, standard headings, no skill bars, icons, or text boxes.
- The strongest achievements sit in the main body, not a sidebar.
- Balanced pages, at most 2.
- Restrained bold (at most one phrase per bullet).
- If the file is a PDF, check the text-extraction order. Sidebars that come out of order are an ATS risk.

**Content Relevance: is the information the right information?**
- A skills section containing every tool mentioned in the experience section.
- Accurate tool names (Azure → Azure DevOps).
- Current tools expected for the role, suggested only as "add if true".
- Nothing irrelevant or risky: date of birth, photo, outdated hobbies, generic soft-skill lists, objective statements.
- A keyword headline instead of an objective.

**Grammar and Syntax: is it clean and consistent?**
- Tense consistency (present for current roles, past for ended ones).
- No bloated or buzzword phrasing, correct acronyms (RTM = Requirements Traceability Matrix).
- Spacing, "&"/"and" consistency, capitalization of product names, https links.
- No overstatement ("proven authority", "architect of").

**Impact: will a recruiter remember it?**
- Quantified results: time saved, % improvements, counts, frequency, team size.
- Recognizable clients or brands named.
- At least one concrete story (a framework built, a pipeline rescued, a critical bug caught).
- Without numbers, Impact scores at most 6, no matter how well it's written.

## Scoring anchors

| Score | Meaning |
|---|---|
| 9–10 | Ready to send; nearly every bullet quantified; tightly targeted |
| 7–8 | Strong; minor gaps in metrics or focus |
| 5–6 | Solid raw material, but generic, unquantified, or badly structured |
| 3–4 | Major structure or relevance problems |
| 1–2 | Not usable for the target role |
