# JobKit — Resume Tailoring Workflow

A step-by-step guide to score, rewrite, and tailor a resume for any job posting —
first by hand, then automated with a reusable skill.

---

## Overview

The flow has three phases. Do them in order the first time; after that you only
need Phase 3.

| Phase | What you do | Output |
|-------|-------------|--------|
| 1. Baseline | Score your current resume and fix its weak spots | A clean, high-scoring base resume |
| 2. Tailor | Match that resume to one specific job description | One tailored resume |
| 3. Automate | Turn the manual steps into a skill + bulk job list | Many tailored resumes in one go |

**Before you start, you need:**
- Your current resume (PDF or DOCX)
- Google Chrome with the [Jobalytics](https://chromewebstore.google.com/) extension
- An AI agent — Claude or ChatGPT
- A job posting on Naukri or LinkedIn

---

## Phase 1 — Score and fix your base resume

### Step 1. Extract missing keywords

1. Open the job posting on Naukri or LinkedIn.
2. Run the **Jobalytics** Chrome extension against the posting with your resume loaded.
3. It returns a list of **missing keywords** — copy them into a scratch file. You will need them in Phase 2.

### Step 2. Get a scored review of your resume

1. Open Claude or ChatGPT.
2. Upload your resume.
3. Send **Prompt 1** below.
4. You get a scorecard out of 10 across six categories.

> **Prompt 1 — Resume review**
>
> ```text
> Provide a detailed review in the following format:
>
> 1. Overall Result: [Score out of 10]
> 2. Effectivity: [Score out of 10] with feedback on how effectively the resume presents the applicant's skills and experiences.
> 3. Layout and Design: [Score out of 10] with comments on the visual appeal and organization of the resume.
> 4. Content Relevance: [Score out of 10] with insights on the relevance and adequacy of the information provided.
> 5. Grammar and Syntax: [Score out of 10] with observations on the language quality and readability.
> 6. Impact: [Score out of 10] with thoughts on how the resume stands out or catches attention.
>
> Use symbols like ✅ for positive aspects and 🙈 for areas of improvement.
> ```

### Step 3. Rebuild until every score is above 7

In the same chat, send:

> ```text
> Prepare the new fresh resume by making sure that all the points are greater than 7.
> ```

Keep this rebuilt resume — it is your **base resume** for every job from now on.

---

## Phase 2 — Tailor the resume to one job

### Step 4. Feed in the job description

1. Go back to the job on Naukri or LinkedIn.
2. Copy the full job description.
3. In the AI chat, paste: **the job description** + **Prompt 2** + **the missing keywords** from Step 1.

> **Prompt 2 — Keyword-matched tailoring**
>
> ```text
> First, analyze the job description to extract essential skills, requirements, and
> frequently mentioned keywords. Cross-reference these with the existing content of the
> resume. Identify areas in the resume where these skills and keywords can be incorporated
> or emphasized, ensuring they match the individual's true experience and qualifications.
> Modify the resume by including these keywords in a way that enhances its relevance to the
> job description. Ensure the final resume remains coherent, professional, and accurately
> reflects the individual's capabilities. Provide the updated resume with highlighted changes
> that align closely with the tailored job description.
> ```

### Step 5. Clean up the output

The agent returns the updated resume. Before using it:

- [ ] Remove all em dashes (—) — they read as AI-generated.
- [ ] Verify every added keyword reflects experience you actually have.
- [ ] Check formatting survived the copy-paste.

At this point you have one tailored resume. Repeating Steps 4–5 by hand for every
job is the slow part — Phase 3 removes it.

---

## Phase 3 — Automate it with a skill

### Step 6. Ask the agent to build the skill

Send this to Claude:

> ```text
> Create a skill file where I will give you job descriptions in a simple list format
> (Excel or CSV). You need to read it and create a proper skill file for me, so that every
> time I give you job descriptions you repeat the resume creation process.
>
> I will give you: "Older resume" + "Job descriptions in CSV or XLSX"
> You give me: an updated resume as a Google Doc file.
> ```

### Step 7. Install the skill in this repo

The generated skill lives at [Skill_ResumeCreator/resume-tailor/](Skill_ResumeCreator/resume-tailor/):

```
resume-tailor/
├── SKILL.md                  # the skill definition
├── Old Resume/               # your base resume from Step 3
├── Jobs/                     # job description spreadsheets
├── Tailored Resumes/         # generated output
├── references/               # writing rules + review rubric
├── scripts/                  # parse_jobs.py, keyword_coverage.py
└── assets/                   # resume + job description templates
```

### Step 8. Bulk-collect job descriptions

1. Install the **Claude Chrome extension**.
2. Open the LinkedIn or Naukri job listing page.
3. Ask it:

> ```text
> Can you fetch all the job descriptions for all the job openings listed here and give me
> a proper CSV/XLSX file with the company name and description?
> ```

4. Save the file into `resume-tailor/Jobs/`.

### Step 9. Generate resumes in bulk

Hand the skill your base resume and the spreadsheet from Step 8. It runs Steps 4–5
for every row and writes one tailored resume per job into `Tailored Resumes/`.

---

## Quick reference

| Need | Go to |
|------|-------|
| Score my resume | [Step 2](#step-2-get-a-scored-review-of-your-resume) |
| Tailor for one job | [Step 4](#step-4-feed-in-the-job-description) |
| Tailor for many jobs | [Step 8](#step-8-bulk-collect-job-descriptions) |
| Prompt 1 (review) | [Step 2](#step-2-get-a-scored-review-of-your-resume) |
| Prompt 2 (tailoring) | [Step 4](#step-4-feed-in-the-job-description) |
