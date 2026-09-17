---
name: resume-tailor
description: Tailor a base resume to one or more job descriptions and deliver every tailored version as its own Google Doc in the user's Google Drive, with changes highlighted and an ATS keyword gap analysis. Use this skill whenever the user shares a resume (PDF, Word, Google Doc, or pasted text) together with a job description, a list of job requirements, a "missing keywords" list, or an Excel/CSV sheet of job postings, or asks to tailor, customize, match, keyword-optimize, or make versions of a resume for jobs. Also use it for scored resume reviews and for rebuilding a resume from scratch. Trigger even when the user doesn't mention Google Docs or this skill by name.
---

# Resume Tailor

Turn one base resume plus N job descriptions into N tailored, truthful, ATS-friendly resumes, each saved as a separate Google Doc.

The goal is interviews the candidate can win. A keyword the candidate can't defend in an interview costs more than it gains, so the truthfulness rules in `references/writing_rules.md` outrank keyword coverage every time.

## Inputs

- **Base resume:** a PDF or DOCX upload, a Google Doc (link or name), or pasted text.
- **Jobs**, in any of these forms:
  - An Excel or CSV file based on `assets/job_descriptions_template.xlsx` (one row per job).
  - Any other spreadsheet: one row per job with headers, or one sheet per job holding a plain list.
  - Pasted job description text or bullet lists.
- **Optional:** "missing keywords" from an ATS scanner such as Jobscan, either per job or for all jobs.

If the resume or the jobs are missing, ask for them in one short question. Don't ask anything else up front.

Keep all working files in `/home/claude/work/`.

## Workflow

### 1. Make sure Google Drive is connected

Call `tool_search` with "Google Drive create file". If no Drive tools load, call `search_mcp_registry` with `["google drive"]`, then `suggest_connectors`, and stop until the user connects. If the user doesn't want Drive, use the fallback at the end of this file.

### 2. Read the base resume and build a fact base

- **PDF:** `pdftotext -layout file.pdf -`
- **DOCX:** `pandoc -t plain file.docx`
- **Google Doc:** Google Drive `read_file_content` (use `search_files` first if you only have a name). Always read the latest version; users often fill placeholders or edit after a doc was created.

Save the plain text as `/home/claude/work/resume.txt`. Then write `/home/claude/work/facts.md` listing:
- contact details
- every employer, title, and date range
- each client or project with dates
- tools, platforms, domains
- certifications with years, and education
- every number or metric

This file is the only source of truth for what the candidate has done.

While reading, note internal problems to raise in the report. Common ones:
- a claimed duration that conflicts with the dates ("sole owner for 5 years" on a 10-year project)
- mismatched counts ("4–5 mentored" in one place, "4" in another)
- ended projects still written in present tense
- leftover brackets or blanks (`[2013]`, "covering  UI tests")
- numbers so small they undersell

### 3. Parse the jobs

For a spreadsheet:

```bash
python scripts/parse_jobs.py <jobs file> -o /home/claude/work/jobs.json
```

The script prints each detected job. If it finds 0 jobs or the fields look wrong, inspect the file with `markitdown <file>` and write `jobs.json` by hand in the same shape (see the script's docstring). For pasted text, write `jobs.json` yourself, putting the raw text in `full_text` and extracted lists in the other fields.

Tell the user in one line how many jobs you found (company – title), then continue without waiting.

### 4. Analyze each job

For each job, work out:
- **Must-haves, nice-to-haves, core duties, and the role level**: individual contributor or lead, and whether it has direct reports.
- **Keywords**: tools, platforms, testing types, process terms, soft skills, and phrases the job description repeats. Run the coverage check to see what the base resume already contains:

```bash
python scripts/keyword_coverage.py /home/claude/work/jobs.json /home/claude/work/resume.txt --job <id>
```

The script is a rough string matcher. Use your own judgment for synonyms it misses.

Then classify every keyword against `facts.md`:

| Class | Meaning | Action |
|---|---|---|
| **Match** | Already in the resume | Keep it; move it higher or switch to the job's exact wording |
| **Reframe** | The experience exists under other words | Rewrite using the job's term, e.g. "translated backlog items into test scenarios" → "identified positive and negative test conditions from user stories" |
| **Likely** | Standard practice implied by documented work, e.g. browser DevTools for a web automation engineer, MS Office | Add it, highlight yellow, ask the user to confirm |
| **Gap** | No evidence: a tool never used, a certification not held, a module or domain never touched | Do **not** add it; report it with honest advice |

User-supplied missing keywords go through the same classification. A keyword being on the list doesn't make it true.

### 5. Write each tailored resume

Before the first resume of the session, read `references/writing_rules.md`. Build from `assets/resume_template.html`, which follows the Google Docs import constraints.

Tailoring moves, most valuable first:
1. **Headline** mirrors the target job title and the job's top 2–3 themes. It is positioning only; never change real job titles.
2. **Summary** of 3–4 sentences, leading with the must-haves the candidate genuinely has.
3. **Core Skills** regrouped so the job's categories and terms come first. Drop low-relevance tools to keep focus.
4. **Bullets** reordered so job-relevant ones lead each role, reworded in the job's language, with every real metric kept.
5. **Role-level fit.** For individual-contributor roles, reframe "lead" duties as supporting and mentoring without changing the title. For lead roles, surface team size, ownership, and decisions.
6. **Additional section** for work-setup requirements (time zones, shift hours, languages). Highlight yellow if unconfirmed.

Every job gets a **review copy** using these highlight conventions:
- **Green** `<span style="background-color:#c8f7c5;">`: text added or changed for this job.
- **Yellow** `<span style="background-color:#fff59d;">`: needs the candidate's confirmation. This covers Likely skills, unconfirmed availability, slots like `[module names]`, and suspected inconsistencies.
- The template's review note box at the top explains the colors.

Save each version as `/home/claude/work/<job id>.html`, then re-run the coverage check against it:

```bash
python scripts/keyword_coverage.py /home/claude/work/jobs.json /home/claude/work/<job id>.html --job <id>
```

Every Match, Reframe, and Likely keyword should now be covered. Gaps stay uncovered. Finish with the checklist at the end of `writing_rules.md`.

### 6. Upload to Google Drive

- **Several jobs:** first create a folder with `create_file`, title `<Candidate> - Tailored Resumes - <YYYY-MM-DD>` and `contentMimeType` `application/vnd.google-apps.folder`. Pass its `id` as `parentId` for each upload. If folder creation fails, upload without a folder.
- **Each job:** call `mcp__Google_Drive__create_file` with:
  - `title`: `<Candidate Name> - <Job Title> - <Company> (tailored, review copy)`
  - `contentMimeType`: `text/html`
  - `textContent`: the full HTML
- Leave `disableConversionToGoogleType` unset; the conversion is what turns the HTML into a Google Doc.
- Send HTML inline as `textContent`. Don't base64-encode a .docx, because retyping long base64 by hand corrupts files.
- Never overwrite, rename, or trash the user's base resume.

**Clean copy.** Make one only when the user asks for a final or clean version, normally after confirming the yellow items. Use the same HTML without the review note and highlight spans, and title it `... (final)`.

### 7. Report back

With several jobs, open with a summary table: Job | Google Doc link | Keyword coverage before → after | Gaps not added.

Then, for each job:
1. **What the job wants:** 2–3 sentences on level, must-haves, and the most-repeated keywords.
2. **Cross-reference table:** Requirement | In the resume before | What I did.
3. **User-supplied missing keywords:** where each one went, or why it wasn't added.
4. **Please confirm:** every yellow item plus inconsistencies from step 2.
5. **Before sending:**
   - Delete the review note.
   - Press Ctrl+A, click the highlighter icon in the toolbar, and choose **None**.
   - Download with File → Download → PDF.

For batches of more than 3 jobs, keep each section to the tables and the confirm list so the reply stays readable.

## Scored reviews and fresh rebuilds

When the user asks to review or score a resume, or to rebuild one without a target job, read `references/review_rubric.md` and use its output format. A fresh rebuild uses the same template and rules with no job targeting. Put yellow `[X]` placeholders where metrics are missing, and never invent numbers.

## Fallback without Google Drive

Read the docx skill, build a .docx with the same content and green/yellow highlights, save it to `/mnt/user-data/outputs/`, and call `present_files`. Tell the user they can open it in Google Docs through File → Open → Upload.
