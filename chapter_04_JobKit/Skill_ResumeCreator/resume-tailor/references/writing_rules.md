# Writing Rules for Tailored Resumes

## Contents
1. Truthfulness
2. ATS-safe structure
3. Language and style
4. Google Docs HTML import constraints
5. Final checklist

---

## 1. Truthfulness (highest priority)

Recruiters test keywords in interviews, and background checks verify titles, dates, and certifications. One false claim can cost an offer, or a job after it's been accepted. Treat everything outside `facts.md` as unproven.

**Never:**
- Add a tool, programming language, framework, platform, certification, degree, domain, employer, or job title that isn't in `facts.md`.
- Change real job titles or dates. The headline may position the candidate ("Senior QA Analyst"); the experience section keeps the actual title.
- Invent or inflate metrics. If a number would help and is missing, use a yellow `[X]`.
- Claim module-level experience the facts don't show. If the facts say "MS Dynamics 365" and the job wants "Dynamics 365 Finance / ERP", write a yellow slot such as `[module names, e.g., Sales / Customer Service / Finance]` instead of claiming ERP.
- Upgrade the strength of a claim ("familiar with" → "expert", "participated" → "led").

**Allowed:**
- Using the job description's term for the same work ("bug tracking" for "defect management", "UI/UX testing" for "validated UI against Figma designs").
- Expanding names when the meaning is clear ("Azure" in a test-management list → "Microsoft Azure DevOps (ADO)"). If it's ambiguous, highlight yellow.
- Surfacing the implied parts of documented work (test plans + RTM + reports → "QA documentation").
- Using an umbrella term that genuinely covers the documented practice (Scrumban → Kanban; API testing between services → integration testing).
- Adding standard practices strongly implied by documented work, always highlighted yellow for confirmation.

**Gaps:** list them in the report with an honest option for each:
- a transferable skill the candidate already has ("Playwright experience maps closely to Cypress")
- a course or certification to consider
- "add it only if you have actually used it"

**Weak numbers:** if a real number undersells the candidate (for example "5+ defects" across a multi-month project), suggest dropping the number rather than keeping it.

---

## 2. ATS-safe structure

- One column. No layout tables, text boxes, images, icons, skill bars, or side columns.
- Standard headings, in this order: Professional Summary, Core Skills, Professional Experience, Education & Certification, Additional.
- Contact line: City, Country | phone | email | LinkedIn | GitHub/portfolio. Link with `https://`, but display the address without the protocol.
- Each important keyword should appear in Core Skills **and** in at least one bullet, since the bullet shows it was actually used. More than about 3 uses of the same term reads as stuffing.
- Give key terms both forms once: "Microsoft Azure DevOps (ADO)", "requirements traceability matrix (RTM)".
- Two pages maximum. Arial 10pt body text.
- Remove date of birth, photo, marital status, generic soft-skill lists, and objective statements.
- Dates as `Mon YYYY – Mon YYYY` or `Mon YYYY – Present`.
- Keep reverse-chronological order of employers. Within one employer, put the most job-relevant client or project first when dates overlap.

---

## 3. Language and style

- Start each bullet with a strong verb. One idea per bullet, 1–2 lines long.
- **Tense:** present for current roles and projects, past for ended ones. Re-check whenever the user edits end dates.
- **Bullet pattern:** action + scope + tool or method + result, with a number where one exists.
  - Weak: "Responsible for regression testing."
  - Strong: "Reduced full regression time from 5 days to 3 hours by automating 80% of high-risk test cases in Jenkins CI."
- No self-praise labels ("proven authority", "architect of", "trusted", "passionate"). Show evidence instead.
- Summary: 3–4 sentences, no "I", no objective statement, numbers where real.
- Consistency:
  - "&" in headings and labels, "and" in sentences
  - en dash (–) in date ranges
  - Oxford comma
  - the same count everywhere a number repeats
- Proper names: JavaScript, TypeScript, Log4j, iOS, GitHub, Microsoft Dynamics 365, Salesforce, Postman, REST Assured, "Three Amigos". Write Jira/JIRA the way the target job description does.
- Fix grammar in text the user wrote, e.g. "flagging almost every requirement and design gaps" → "catching most requirement and design gaps".
- Match the job description's spelling (US or UK) when it's clearly one or the other.

---

## 4. Google Docs HTML import constraints

Google Drive converts uploaded `text/html` into a Google Doc. What converts reliably:

- **Works:** `<p>`, `<h2>`, `<b>`, `<i>`, `<ul>`/`<li>`, `<a href>`, and `<span>` with inline `font-size`, `font-weight`, `color`, and `background-color`. Also `margin`, a paragraph `border` or `border-bottom`, and `text-align:center`.
- **Use inline styles only.** `<style>` blocks and classes are dropped or unreliable.
- **Avoid:** tab stops or right-aligned dates on the same line (put dates on their own italic line), flex or grid, layout tables, remote images, and `position`.
- Escape `&` as `&amp;`, and `<` / `>` inside text.
- Use `&nbsp;|&nbsp;` for separators so spacing survives.
- Highlight colors: green `#c8f7c5` for changed text, yellow `#fff59d` for text to confirm.

---

## 5. Final checklist before upload

- [ ] Every claim traces to `facts.md` or is highlighted yellow.
- [ ] No Gap keyword was added.
- [ ] No stray `[X]` or brackets except intentional yellow placeholders.
- [ ] Tenses match the dates; counts and durations agree across summary and bullets.
- [ ] The coverage check was re-run on the final HTML.
- [ ] About 2 pages (roughly 700–900 words of body text).
- [ ] The review note box is present in the review copy and absent in a clean copy.
- [ ] Real job titles, employers, and dates are unchanged.
