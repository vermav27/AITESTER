# AITESTER

AI Engineering resources for Software QA / SDET work. This repository combines LLM basics, prompt engineering templates, a Playwright automation framework example, and a local AI application that generates test cases from Jira tickets.

> This README is the top-level map of the repository. Individual projects, such as the Playwright framework and the Jira generator, also include their own README files with deeper setup and usage details.

---

## What's Inside

| Area | Purpose |
|---|---|
| `chapter_01_LLM_Basics/` | Grounding rules for safer QA-focused LLM output. |
| `chapter_02_Prompt_Engineering/` | RICE-POT prompt framework, reusable prompt templates, and the OrangeHRM Playwright framework example. |
| `chapter_03_Local_TestCase_Generator/` | Local Python + Streamlit Jira AI Test Case Generator using Ollama, with optional Groq support. |
| `PromptQuickReference.md` | Quick decision guide for selecting the right prompt template. |

---

## Repository Structure

```text
AITester/
├── README.md
├── PromptQuickReference.md
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
└── chapter_03_Local_TestCase_Generator/
    ├── source/
    │   ├── Prompt.md
    │   ├── finetuned_Prompt.md
    │   └── roughAppDiagram.png
    ├── template/
    │   └── testcase_creator.md
    └── jira-ai-testcase-generator/
        ├── README.md
        ├── app.py
        ├── pages/
        │   └── settings.py
        ├── services/
        │   ├── jira_service.py
        │   ├── ollama_service.py
        │   ├── groq_service.py
        │   └── llm_service.py
        ├── utils/
        │   ├── config_manager.py
        │   ├── jira_parser.py
        │   ├── prompt_builder.py
        │   └── template_loader.py
        ├── templates/
        │   └── test_case_template.md
        └── requirements.txt
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
- Rotate any token that has ever been committed, shared, pasted into an AI chat, or exposed in logs.
- Generated artifacts and dependency folders should remain uncommitted.

---

## Recommended Learning Path

1. Start with `chapter_01_LLM_Basics/Rules_AntiHallucination.md`.
2. Learn the RICE-POT structure in `chapter_02_Prompt_Engineering/01_RICE_POT_Template.md`.
3. Try the prompt templates using `PromptQuickReference.md`.
4. Explore the OrangeHRM Playwright framework as a full automation example.
5. Run the Jira AI Test Case Generator from Chapter 3 and customize `templates/test_case_template.md` for your team.
