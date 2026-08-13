# AITESTER

AI Engineering — prompt engineering resources and templates for Software QA / SDET work. This repository contains learning chapters and reusable, copy-paste prompt templates for generating test cases, API tests, and bug reports with LLMs.

> **Note:** This README is maintained on a regular basis and updated whenever new folders, chapters, or templates are added to the repository.

---

## Repository Structure

```
AITester/
├── README.md                              # This file — project overview & structure guide
├── PromptQuickReference.md                # Quick guide for picking the right prompt template
├── chapter_01_LLM_Basics/                 # Chapter 1 — LLM fundamentals & constraints
│   └── Rules_AntiHallucination.md         # Anti-hallucination rules for QA assistant prompts
├── chapter_02_Prompt_Engineering/         # Chapter 2 — prompt engineering & templates
│   ├── 01_RICE_POT_Template.md            # RICE-POT prompt framework template (Role/Instruction/Context/Example/Parameters/Output/Tone)
│   ├── 02_RICE_POT_example.md             # RICE-POT worked example — OrangeHRM Playwright framework build
│   ├── OrangePlaywrightFramework/         # Enterprise JS/Playwright OrangeHRM automation framework (POM, XPath only)
│   └── Prompt_Template/                   # Copy-paste prompt templates (by category)
│       ├── BasicTestCasePrompts/          # Functional test case templates
│       ├── APITestingPrompts/             # API test templates
│       └── BugsRelatedPrompts/            # Bug report & analysis templates
├── .gitignore                             # Ignores .commandcode/ local session state
└── .commandcode/                          # Local session state (not versioned)
```

---

## Chapters

### chapter_01_LLM_Basics

| File | Description |
|---|---|
| `Rules_AntiHallucination.md` | Mandatory rules that keep LLM outputs grounded in provided input (PRD, API docs, logs, screenshots, test data). Prohibits inventing features/APIs/error codes, requires labeling inferred details as low-confidence, and enforces a strict 4-step output format: Verified Facts → Missing/Unknown → Generated Output → Self-Validation Check. |

### chapter_02_Prompt_Engineering

Prompt engineering workflows and the template library.

| File / Folder | Description |
|---|---|
| `01_RICE_POT_Template.md` | The RICE-POT prompt framework — a structured template with 7 sections: **R**ole, **I**nstructions, **C**ontext, **E**xample, **P**arameters, **O**utput, **T**one — plus a Final Validation checklist to keep LLM outputs grounded and complete. |
| `02_RICE_POT_example.md` | Worked example of the RICE-POT framework: a filled-in prompt that builds an enterprise JavaScript/Playwright automation framework for OrangeHRM (the resulting code lives in `OrangePlaywrightFramework/`). |
| `OrangePlaywrightFramework/` | Enterprise-level JavaScript/Playwright automation framework for OrangeHRM (Page Object Model, XPath-only locators, timestamped screenshot/log/report artifacts, 99% pass-rate gate). Its own README explains architecture, setup, and commands. |
| `Prompt_Template/` | All reusable prompt templates, organized into 3 categories (see below). |

---

## Prompt Templates

Templates follow a consistent structure: **ROLE → TASK → CONSTRAINTS → FORMAT**, and most end with `+ ANTI HALLUCINATION RULES` to enforce grounded, evidence-only output.

| Category (Folder) | Templates | Purpose |
|---|---|---|
| **BasicTestCasePrompts** | `BasicTestCaseGeneration.txt` — Basic Test Case Generation (RTCFR)<br>`PRDToTestCaseGeneration.txt` — PRD to Test Cases (Comprehensive)<br>`APITestCaseGeneration.txt` — API Test Case Generation<br>`NegativeTestCaseOnly.txt` — Negative Test Cases Only<br>`RegressionTestSuite.txt` — Regression Test Suite | Functional test cases from requirements, PRDs, API docs; negative-only scenarios; regression suites. |
| **APITestingPrompts** | `RestAPITestSuite.txt` — REST API Test Suite<br>`APIValidationTest.txt` — API Validation Tests<br>`APIAuthenticationTest.txt` — API Authentication Tests<br>`APIContractTestng.txt` — API Contract Testing<br>`APIPerformaceTestScenario.txt` — API Performance Test Scenarios<br>`APIErrorHandlingTest.txt` — API Error Handling Tests | Full REST suites, input validation, auth/security, contract/schema checks, performance scenarios, and error handling. |
| **BugsRelatedPrompts** | `BugReportFromEvidence.txt` — Basic Bug Report from Evidence<br>`BugClassification.txt` — Bug Classification<br>`BugAnalysisChainOfThoughts.txt` — Bug Analysis (Chain-of-Thought)<br>`ConvertToBugFromNotes.txt` — Convert Notes to Bug Report | Structured bug reports from evidence, severity/priority classification, root-cause analysis, and notes-to-report conversion. |

> **Tip:** Use [`PromptQuickReference.md`](./PromptQuickReference.md) to decide which template fits your task. It includes a per-template "Best For / Use When" table and a Quick Decision Matrix.

---

## How to Use a Template

1. Open the matching `.txt` template from `chapter_02_Prompt_Engineering/Prompt_Template/<category>/`.
2. Copy the content into your LLM chat.
3. Replace the placeholders — `[PASTE ...]`, `[FEATURE]`, `[MODULE]`, `[NUMBER]`, etc.
4. Paste the required documentation (SRS/PRD, API docs, logs, screenshots description) where indicated.
5. The template's constraints and anti-hallucination rules keep the output grounded and repeatable.
