# AITESTER

AI Engineering resources for Software QA / SDET work. This repository combines LLM basics, prompt engineering templates, a Playwright automation framework example, a local AI application that generates test cases from Jira tickets, a resume-tailoring skill, a React job-application tracker, a Flask agent that turns a Jira ticket into a review-ready test plan, and agent skills for drafting review-ready test plans and for turning an idea into LinkedIn and Medium content.

> This README is the top-level map of the repository. Individual projects, such as the Playwright framework and the Jira generator, also include their own README files with deeper setup and usage details.

---

## What's Inside

| Area | Purpose |
|---|---|
| `chapter_01_LLM_Basics/` | Grounding rules for safer QA-focused LLM output. |
| `chapter_02_Prompt_Engineering/` | RICE-POT prompt framework, reusable prompt templates, and the OrangeHRM Playwright framework example. |
| `chapter_03_Local_TestCase_Generator/` | Local Python + Streamlit Jira AI Test Case Generator using Ollama, with optional Groq support. |
| `chapter_04_JobKit/` | Resume-tailoring skill that turns one base resume plus a sheet of job descriptions into tailored, ATS-friendly versions. |
| `chapter_05_JobTracker/` | NextGen Job Tracker: a local-first React + TypeScript single-page app with a Kanban board, dashboard metrics, and an in-app user guide viewer. |
| `chapter_06_Branding_LinkedIn_Medium/` | LinkedIn and Medium content skill, plus the generated content packs in `Output/`. |
| `chapter_07_Basics_AI_Agents/` | B.L.A.S.T. agent build: a Flask app that turns a Jira ticket into a review-ready test plan using local Ollama. |
| `.agents/skills/testplan-create/` | Codex skill for fetching Jira tickets, analyzing requirement gaps, and drafting test plans. |
| `.agents/output/` | Generated local artifacts such as Markdown/PDF test plans and reviewed design attachments. |
| `PromptQuickReference.md` | Quick decision guide for selecting the right prompt template. |

---

## Repository Structure

```text
AITester/
├── README.md
├── PromptQuickReference.md
├── .agents/
│   ├── output/
│   │   ├── KAN-1-Design.png
│   │   ├── KAN-1-test-plan.md
│   │   └── KAN-1-test-plan.pdf
│   └── skills/
│       └── testplan-create/
│           ├── SKILL.md
│           ├── .env          # local only; do not commit real secrets
│           ├── assets/
│           │   ├── logo.png
│           │   └── vwo_details.md
│           ├── references/
│           │   ├── requirement-checklist.md
│           │   └── template/
│           │       └── Test_Plan_Template.md
│           └── scripts/
│               └── fetch_jira.sh
├── chapter_01_LLM_Basics/
│   └── Rules_AntiHallucination.md
├── chapter_02_Prompt_Engineering/
│   ├── 01_RICE_POT_Template.md
│   ├── 02_RICE_POT_example.md
│   ├── Task_Testcase_Using_Ollama/
│   │   └── Task_Testcase_Using_Ollama.md
│   ├── OrangePlaywrightFramework/
│   │   ├── README.md
│   │   ├── Base/
│   │   ├── Pages/
│   │   ├── Selectors/
│   │   ├── Tests/
│   │   ├── Utils/
│   │   ├── config/
│   │   ├── package.json
│   │   └── playwright.config.js
│   └── Prompt_Template/
│       ├── APITestingPrompts/
│       ├── BasicTestCasePrompts/
│       └── BugsRelatedPrompts/
├── chapter_03_Local_TestCase_Generator/
│   ├── source/
│   │   ├── Prompt.md
│   │   ├── finetuned_Prompt.md
│   │   └── roughAppDiagram.png
│   ├── template/
│   │   └── testcase_creator.md
│   └── jira-ai-testcase-generator/
│       ├── README.md
│       ├── app.py
│       ├── pages/
│       │   └── settings.py
│       ├── services/
│       │   ├── jira_service.py
│       │   ├── ollama_service.py
│       │   ├── groq_service.py
│       │   └── llm_service.py
│       ├── utils/
│       │   ├── config_manager.py
│       │   ├── jira_parser.py
│       │   ├── prompt_builder.py
│       │   └── template_loader.py
│       ├── templates/
│       │   └── test_case_template.md
│       └── requirements.txt
├── chapter_04_JobKit/
│   ├── Prompts.md
│   └── Skill_ResumeCreator/
│       └── resume-tailor/
│           ├── SKILL.md
│           ├── assets/
│           │   ├── job_descriptions_template.xlsx
│           │   └── resume_template.html
│           ├── references/
│           │   ├── review_rubric.md
│           │   └── writing_rules.md
│           ├── scripts/
│           │   ├── keyword_coverage.py
│           │   └── parse_jobs.py
│           ├── Jobs/
│           │   └── Jobs_17Sept.xlsx
│           ├── Old Resume/
│           │   └── Vineet Verma_10yr_Resume.pdf
│           └── Tailored Resumes/
│               ├── facts.md
│               └── *.html                  # per-job review copies
├── chapter_05_JobTracker/
│   ├── 1_BasicStarting_ImprovisedPrompt.md
│   ├── 2_TabsPrompt.md
│   ├── 3_Prompt_DownloadOption.md
│   ├── BasicStarting_Prompt.md
│   └── NextGenJobTracker/
│       ├── README.md
│       ├── index.html
│       ├── package.json
│       ├── vercel.json
│       ├── src/
│       │   ├── App.tsx
│       │   ├── components/
│       │   └── services/
│       ├── tests/
│       ├── docs/
│       │   └── SESSION_LOG.md
│       └── Architecture/
│           ├── Architecture.png
│           └── NextGenJobTracker_User_Guide.pdf
├── chapter_06_Branding_LinkedIn_Medium/
│   ├── Skill_LinkedInMedium_PostCreator/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── brand-voice.md
│   │   │   ├── example-pack.md
│   │   │   ├── hooks.md
│   │   │   ├── image-prompts.md
│   │   │   ├── linkedin-post.md
│   │   │   ├── medium-article.md
│   │   │   └── ImageReference/
│   │   │       └── Reference.png
│   │   └── scripts/
│   │       └── lint_content.py
│   └── Output/
│       ├── README.md
│       ├── 01-hooks.md
│       ├── 02-linkedin-post.md
│       ├── 03-linkedin-card-prompt.md
│       ├── 04-medium-article.md
│       └── 05-medium-header-prompt.md
└── chapter_07_Basics_AI_Agents/
    └── Test-Plan-Agent-Blast/
        ├── README.md
        ├── BLAST.md                  # governing protocol
        ├── PromptUsed.md
        ├── task_plan.md              # phases, goals, checklists
        ├── findings.md               # Jira research, endpoints, defects found
        ├── progress.md               # append-only run log
        ├── llm.md                    # constitution: schemas, rules, invariants
        ├── run.py                    # Flask entry point
        ├── requirements.txt
        ├── .env.example
        ├── app/                      # Flask presentation layer
        │   ├── __init__.py           # create_app() factory + markdown filter
        │   ├── routes/               # main + settings blueprints
        │   ├── templates/            # base, index, settings
        │   └── static/               # css, js
        ├── core/                     # deterministic engine + agent
        │   ├── config_manager.py
        │   ├── jira_client.py
        │   ├── normalize.py
        │   ├── checklist.py
        │   ├── ollama_client.py
        │   ├── render.py
        │   ├── agent.py
        │   └── navigation.py
        ├── tools/                    # L3 CLIs (fetch, normalize, gaps, render, run)
        ├── architecture/             # Layer-1 SOPs
        ├── prompts/
        │   └── test_plan_prompt.md
        ├── templates/
        │   ├── Test_Plan_Template.md
        │   └── requirement-checklist.md
        └── runs/                     # generated plans (.md + .json)
```

---

## Chapter 1 - LLM Basics

| File | Description |
|---|---|
| `Rules_AntiHallucination.md` | QA-focused anti-hallucination rules that keep LLM output grounded in supplied inputs such as PRDs, API docs, Jira tickets, logs, screenshots, and test data. |

The rules enforce a clear output pattern: verified facts, missing/unknown information, generated output, and self-validation.

---

## Chapter 2 - Prompt Engineering

Chapter 2 contains the reusable prompt library and a worked automation-framework example.

| File / Folder | Description |
|---|---|
| `01_RICE_POT_Template.md` | RICE-POT framework template: Role, Instructions, Context, Example, Parameters, Output, and Tone. |
| `02_RICE_POT_example.md` | Filled RICE-POT example for building the OrangeHRM Playwright framework. |
| `Task_Testcase_Using_Ollama/` | Example test-case output generated with a local Ollama model. |
| `OrangePlaywrightFramework/` | Enterprise-style JavaScript / Playwright automation framework for OrangeHRM using Page Object Model, XPath locators, screenshots, logs, reports, cleanup, and a 99% pass-rate gate. |
| `Prompt_Template/` | Copy-paste prompt templates grouped by QA task type. |

### Prompt Templates

Templates follow a consistent `ROLE -> TASK -> CONSTRAINTS -> FORMAT` style, and most include anti-hallucination constraints so outputs stay evidence-based.

| Category | Templates | Purpose |
|---|---|---|
| `BasicTestCasePrompts/` | `BasicTestCaseGeneration.txt`, `PRDToTestCaseGeneration.txt`, `APITestCaseGeneration.txt`, `NegativeTestCaseOnly.txt`, `RegressionTestSuite.txt` | Functional, PRD-based, API, negative, and regression test-case generation. |
| `APITestingPrompts/` | `RestAPITestSuite.txt`, `APIValidationTest.txt`, `APIAuthenticationTest.txt`, `APIContractTestng.txt`, `APIPerformaceTestScenario.txt`, `APIErrorHandlingTest.txt` | REST suites, validation, authentication/security, contract/schema, performance, and error-handling scenarios. |
| `BugsRelatedPrompts/` | `BugReportFromEvidence.txt`, `BugClassification.txt`, `BugAnalysisChainOfThoughts.txt`, `ConvertToBugFromNotes.txt` | Bug report creation, classification, analysis, and notes-to-bug conversion. |

Use [`PromptQuickReference.md`](./PromptQuickReference.md) when you want a quick "which template should I use?" answer.

### OrangeHRM Playwright Framework Quick Start

```bash
cd chapter_02_Prompt_Engineering/OrangePlaywrightFramework
npm install
npx playwright install chromium
npm test
```

For full architecture, commands, report details, and headed-mode notes, see [`chapter_02_Prompt_Engineering/OrangePlaywrightFramework/README.md`](./chapter_02_Prompt_Engineering/OrangePlaywrightFramework/README.md).

---

## Chapter 3 - Local Test Case Generator

Chapter 3 adds a runnable local application: **Jira AI Test Case Generator**.

The app lets a user type a request such as:

```text
Create test cases for ABC-123
```

It then extracts the Jira issue key, fetches the Jira ticket through the Jira REST API, converts the ticket fields into structured requirement context, loads the test-case template, sends the prompt to an AI provider, and displays generated test cases in Streamlit.

### Key Features

- Two-page Streamlit app: Chat / Test Case Generator and Settings / Configuration.
- Natural-language Jira key extraction, so users do not need a separate Jira ID field.
- Jira REST API integration using base URL, email, and API token from local configuration.
- Local-first generation with Ollama and the Gemma model configured in `.env`.
- Optional Groq provider and Ollama-to-Groq fallback when Groq is configured.
- External output template at `templates/test_case_template.md`.
- Modular service layer for Jira, Ollama, Groq, and provider dispatch.
- Connection tests for Jira, Ollama, and Groq from the Settings page.

### Jira Generator Quick Start

```bash
cd chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Then open the Streamlit URL, usually:

```text
http://localhost:8501
```

Before generating test cases, configure these values from the Settings page or your local `.env` file:

| Variable | Description |
|---|---|
| `JIRA_BASE_URL` | Jira site URL, for example `https://your-domain.atlassian.net`. |
| `JIRA_EMAIL` | Jira account email. |
| `JIRA_API_TOKEN` | Jira API token. Do not use your Jira password. |
| `OLLAMA_BASE_URL` | Local Ollama API URL, usually `http://localhost:11434`. |
| `OLLAMA_MODEL` | Installed Ollama model tag, currently `gemma3:4b`. |
| `GROQ_API_KEY` | Optional Groq API key. |
| `GROQ_MODEL` | Groq model name. |
| `AI_PROVIDER` | `ollama` or `groq`. |
| `ACCEPTANCE_CRITERIA_FIELD_ID` | Optional Jira custom field ID for acceptance criteria. |

For the full application README, architecture diagram, troubleshooting, and validation checklist, see [`chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator/README.md`](./chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator/README.md).

---

## Chapter 4 - JobKit

Where Chapter 3 generates test cases from a ticket, Chapter 4 handles the job-search side: one base resume plus N job descriptions becomes N tailored, ATS-friendly resumes.

| File / Folder | Description |
|---|---|
| `Prompts.md` | Prompts used while building the chapter's job-search tooling. |
| `Skill_ResumeCreator/resume-tailor/SKILL.md` | The `resume-tailor` skill: reads a base resume plus a sheet of job descriptions, then writes one tailored resume per job. |
| `Skill_ResumeCreator/resume-tailor/scripts/parse_jobs.py` | Parses an Excel/CSV job sheet into structured `jobs.json`. |
| `Skill_ResumeCreator/resume-tailor/scripts/keyword_coverage.py` | Rough keyword-coverage check between a job description and a resume. |
| `Skill_ResumeCreator/resume-tailor/references/writing_rules.md` | Truthfulness and writing rules, which outrank keyword coverage every time. |
| `Skill_ResumeCreator/resume-tailor/references/review_rubric.md` | Rubric and output format for scored resume reviews and rebuilds. |
| `Skill_ResumeCreator/resume-tailor/assets/` | HTML resume template and the job-description spreadsheet template. |
| `Skill_ResumeCreator/resume-tailor/Jobs/` | Job-description spreadsheet input. |
| `Skill_ResumeCreator/resume-tailor/Old Resume/` | The original base resume PDF. |
| `Skill_ResumeCreator/resume-tailor/Tailored Resumes/` | Generated per-job review copies, plus `facts.md`: the source of truth for what the candidate has actually done. |

Every keyword is classified as Match, Reframe, Likely or Gap. Gaps are reported with honest advice and never added. In the review copies, added or changed text is highlighted green and anything needing the candidate's confirmation is highlighted yellow.

---

## Chapter 5 - Job Tracker

Chapter 5 is **NextGen Job Tracker**, a local-first single-page React app for running an active job search: a Kanban board, a metrics dashboard, backup and restore, and a five-page user guide bundled into the build.

| File / Folder | Description |
|---|---|
| `NextGenJobTracker/README.md` | Application README: views, storage model, testing, and deployment readiness. |
| `NextGenJobTracker/src/` | `App.tsx`, `components/` (Dashboard, KanbanBoard, JobCard, JobForm, HelpGuide, UserGuideViewer), and `services/` (job logic, dashboard metrics, import/export). |
| `NextGenJobTracker/tests/` | Vitest coverage for dashboard metrics, tab behaviour, the guide viewer, URL and platform handling, dates, import/export and IndexedDB persistence. |
| `NextGenJobTracker/docs/SESSION_LOG.md` | Session log for the build. |
| `NextGenJobTracker/Architecture/` | Architecture diagram and the five-page user guide PDF. |
| `1_BasicStarting_ImprovisedPrompt.md`, `2_TabsPrompt.md`, `3_Prompt_DownloadOption.md`, `BasicStarting_Prompt.md` | The numbered build prompts behind the app. |

Storage is browser-local through IndexedDB (`idb`): no backend, no accounts, no remote database, no analytics. Persistence is tied to one browser profile and origin, so **Export JSON** is the backup mechanism.

```bash
cd chapter_05_JobTracker/NextGenJobTracker
npm install
npm run dev        # http://127.0.0.1:5173
npm run lint
npm test
```

---

## Chapter 6 - Branding (LinkedIn & Medium)

Chapter 6 holds the content engine used to publish on LinkedIn and Medium: one raw idea in, a five-piece pack out.

| File / Folder | Description |
|---|---|
| `Skill_LinkedInMedium_PostCreator/SKILL.md` | The `vineet-qa-content` skill. Turns a title, bullets, notes or an image into 3 controversial hooks, a LinkedIn post, an X-style card prompt, a Medium article and a cyberpunk header prompt. |
| `Skill_LinkedInMedium_PostCreator/references/brand-voice.md` | The fact sheet (the only personal claims allowed), plus voice traits, content pillars, banned words and client-naming rules. |
| `Skill_LinkedInMedium_PostCreator/references/hooks.md` | Hook types, heat levels and the defensibility test. |
| `Skill_LinkedInMedium_PostCreator/references/linkedin-post.md` | LinkedIn spec: 150–300 words, → arrows, one offer, PS sign-off, 3–5 hashtags. |
| `Skill_LinkedInMedium_PostCreator/references/medium-article.md` | Medium spec: 1,000–1,800 words, one table, one code block, one list, pull quote and bio. |
| `Skill_LinkedInMedium_PostCreator/references/image-prompts.md` | Both image prompt templates, plus the topic-to-metaphor table. |
| `Skill_LinkedInMedium_PostCreator/references/example-pack.md` | The approved gold-standard pack, used as the bar for new packs. |
| `Skill_LinkedInMedium_PostCreator/references/ImageReference/Reference.png` | Reference image showing the X-style card format. |
| `Skill_LinkedInMedium_PostCreator/scripts/lint_content.py` | Brand-rule linter for the post, article and card. |
| `Output/` | Generated content packs. See [`Output/README.md`](./chapter_06_Branding_LinkedIn_Medium/Output/README.md). |

### Generated Content Packs

| Pack | Pieces | Folder |
|---|---|---|
| AI influencers — "AI Influencers Are Quietly Taking Over Your Feed. Here Is How People Make Them." | 3 hooks, LinkedIn post, card prompt, Medium article, cyber header prompt | `chapter_06_Branding_LinkedIn_Medium/Output/` |

Lint a pack before publishing. The linter reads raw text, so the post is piped in from its copy-paste block:

```bash
cd chapter_06_Branding_LinkedIn_Medium/Skill_LinkedInMedium_PostCreator
awk '/^```text$/{f=1;next} /^```$/{f=0} f' ../Output/02-linkedin-post.md | python3 scripts/lint_content.py linkedin -
python3 scripts/lint_content.py medium ../Output/04-medium-article.md
python3 scripts/lint_content.py card ../Output/03-linkedin-card-prompt.md
```

---

## Chapter 7 - Basics of AI Agents (B.L.A.S.T. Test Plan Agent)

Chapter 7 is the agent-building chapter: **Test Plan Agent**, a Flask application that turns a Jira
ticket into a review-ready test plan using a locally installed Ollama model. It is built on the
B.L.A.S.T. protocol (`Blueprint → Link → Architect → Stylize → Trigger`) and the three-layer
A.N.T. architecture (`Agent` / `Navigation` / `Tools`).

Where Chapter 3 *generates test cases*, Chapter 7 *plans the testing* — and stops at a human review
gate instead of declaring itself finished.

### What It Does

You type a plain-English request such as:

```text
Fetch this Jira and create a test plan for KAN-1
Create a test plan for the latest ticket in KAN
```

The agent then:

1. Resolves the target ticket (explicit key, or the newest ticket in a named project).
2. Fetches the issue and its comments over the Jira REST API **v3** (read-only).
3. Flattens Atlassian Document Format and locates acceptance criteria, recording which source each
   one came from (custom field → description → comment).
4. Runs a deterministic requirement checklist and produces a **Gaps & Questions** list.
5. Drafts the full plan with the local Ollama model.
6. Renders the canonical template, appends the authoritative gaps table and a Human Review Gate,
   writes the artifacts, and **stops** — the status is always `draft`.

### Key Features

- **Two-page Flask UI** — a Generate page and a Settings page, with a pipeline trace and stats.
- **Settings page** — Jira Base URL / Email / token and Ollama URL / model, with one-click
  **Test Jira Connection** and **Test Ollama Connection** buttons.
- **Secrets stay secret** — values live in a gitignored `.env`, are masked in the UI, and never
  appear in a log line or a generated plan.
- **Local-first LLM** — Ollama only; nothing is sent to a cloud model.
- **Deterministic where it matters** — fetching, normalizing, gap analysis, the gaps table, and the
  review gate are computed by code, not by the model.
- **CLI tools** — the same engine is drivable without a browser via `tools/`.
- **Project memory** — `task_plan.md`, `findings.md`, `progress.md`, and `llm.md` hold the phases,
  research, append-only run log, and the frozen schemas/rules/invariants.

### Test Plan Agent Quick Start

```bash
cd chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then fill in your Jira and Ollama values
python run.py
```

Open **http://127.0.0.1:5000**.

Verify both services before generating:

```bash
python tools/verify_connections.py
```

```text
  ✓ jira    Connected to Jira as <you>.
  ✓ ollama  Ollama is running with model 'gemma3:4b'.

Link verified — both services are reachable.
```

Run the pipeline without the browser:

```bash
python tools/analyze_gaps.py KAN-1                              # gap analysis only, no LLM
python tools/run_agent.py "create a test plan for KAN-1"        # whole pipeline
```

Generated plans are written to `runs/` as `<KEY>-test-plan-<timestamp>.md` plus a matching `.json`,
and are downloadable from the UI.

### Configuration Variables

| Variable | Description |
|---|---|
| `JIRA_BASE_URL` | Jira site URL, for example `https://your-domain.atlassian.net`. |
| `JIRA_EMAIL` | Jira account email. Leave blank to send the token as a Bearer PAT instead. |
| `JIRA_TOKEN` | Jira API token. Do not use your Jira password. |
| `JIRA_AC_FIELD_ID` | Optional custom field holding acceptance criteria, e.g. `customfield_10001`. |
| `OLLAMA_BASE_URL` | Local Ollama API URL, usually `http://localhost:11434`. |
| `OLLAMA_MODEL` | Installed Ollama model tag, currently `gemma3:4b`. |
| `APP_HOST` / `APP_PORT` | Optional Flask bind override, default `127.0.0.1:5000`. |

For the full application README — architecture diagram, folder structure, CLI reference,
troubleshooting, and the security notes — see [`chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast/README.md`](./chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast/README.md).

---

## Codex Agent Skill - Test Plan Creator

The `.agents/skills/testplan-create/` skill turns a Jira ticket into a human-review-ready test plan. It is designed for QA/test planning work such as:

```text
Create a test plan for KAN-1
```

The skill flow is:

1. Fetch the Jira ticket using `scripts/fetch_jira.sh` and local Jira environment variables.
2. Capture summary, description, acceptance criteria, components, linked issues, attachments, and release/sprint context where available.
3. Check the ticket against `references/requirement-checklist.md`.
4. Draft the plan using `references/template/Test_Plan_Template.md`.
5. Stop at a Human Review Gate so the test plan is treated as draft/in-review, not final.

### Test Plan Skill Files

| File / Folder | Purpose |
|---|---|
| `.agents/skills/testplan-create/SKILL.md` | Skill instructions and guardrails for Jira-based test-plan drafting. |
| `.agents/skills/testplan-create/scripts/fetch_jira.sh` | Jira REST API helper for fetching issue details. |
| `.agents/skills/testplan-create/references/requirement-checklist.md` | Requirement gap-analysis checklist used before drafting the plan. |
| `.agents/skills/testplan-create/references/template/Test_Plan_Template.md` | Standard test-plan template. |
| `.agents/skills/testplan-create/assets/vwo_details.md` | Structured VWO overview/reference notes. |
| `.agents/skills/testplan-create/assets/logo.png` | Skill asset used for VWO-related context or presentation. |
| `.agents/skills/testplan-create/.env` | Local Jira configuration file. Keep this private and out of commits. |

### Generated Output

Generated plans and supporting artifacts are stored in `.agents/output/`.

Current generated example:

| Artifact | Description |
|---|---|
| `.agents/output/KAN-1-test-plan.md` | Draft Markdown test plan for Jira story `KAN-1`. |
| `.agents/output/KAN-1-test-plan.pdf` | PDF version of the same draft test plan. |
| `.agents/output/KAN-1-Design.png` | Jira design attachment used as a visual reference for the test plan. |

### Test Plan Skill Usage

Before using the skill, configure Jira access locally:

Create `.agents/skills/testplan-create/.env` locally with the required values.

Required variables:

| Variable | Description |
|---|---|
| `JIRA_BASE_URL` | Jira site URL, for example `https://your-domain.atlassian.net`. |
| `JIRA_EMAIL` | Jira account email. |
| `JIRA_TOKEN` | Jira API token. Do not use your Jira password. |

To fetch a ticket manually:

```bash
set -a
source .env
set +a
bash scripts/fetch_jira.sh KAN-1
```

The generated test plan should always include gaps/questions, assumptions, risks, scenario priorities, test data needs, entry/exit criteria, and a Human Review Gate.

---

## How to Use a Prompt Template

1. Open the matching `.txt` file under `chapter_02_Prompt_Engineering/Prompt_Template/<category>/`.
2. Copy the template into your LLM chat.
3. Replace placeholders such as `[PASTE ...]`, `[FEATURE]`, `[MODULE]`, and `[NUMBER]`.
4. Paste the required source material, such as PRD, SRS, API docs, logs, or screenshot descriptions.
5. Review the generated output against the anti-hallucination and validation rules.

---

## Security Notes

- Do not hardcode Jira tokens, Groq keys, emails, or project credentials in source files or documentation.
- Keep real credentials in a local `.env` file only.
- Treat `.env.example` as a placeholder template; it should not contain real secrets.
- Keep `.agents/skills/testplan-create/.env` private and do not commit it.
- Keep `chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast/.env` private and do not commit it; the file is gitignored.
- The Chapter 7 app binds to `127.0.0.1` and has no authentication of its own. Do not expose it publicly.
- The agent is read-only against Jira: it never transitions, comments on, or edits a ticket.
- Review generated files in `.agents/output/` and `chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast/runs/` before sharing or committing them, because Jira tickets and attachments may contain private product details.
- Rotate any token that has ever been committed, shared, pasted into an AI chat, or exposed in logs.
- Generated artifacts and dependency folders should remain uncommitted.

---

## Recommended Learning Path

1. Start with `chapter_01_LLM_Basics/Rules_AntiHallucination.md`.
2. Learn the RICE-POT structure in `chapter_02_Prompt_Engineering/01_RICE_POT_Template.md`.
3. Try the prompt templates using `PromptQuickReference.md`.
4. Explore the OrangeHRM Playwright framework as a full automation example.
5. Run the Jira AI Test Case Generator from Chapter 3 and customize `templates/test_case_template.md` for your team.
6. Use `.agents/skills/testplan-create/` to draft Jira-based test plans and review the generated artifacts in `.agents/output/`.
7. Use `chapter_04_JobKit/Skill_ResumeCreator/resume-tailor/SKILL.md` to tailor a resume per job description, then review the copies in `Tailored Resumes/`.
8. Run `chapter_05_JobTracker/NextGenJobTracker` to track applications end to end, and read its user guide from inside the app.
9. Use the Chapter 6 content skill to turn an idea into a LinkedIn and Medium pack, then lint it before publishing.
10. Read `chapter_07_Basics_AI_Agents/Test-Plan-Agent-Blast/BLAST.md` and `llm.md` to see how an agent project is specified, then run the Chapter 7 Test Plan Agent to draft a plan for a real ticket.
