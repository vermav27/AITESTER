# Prompt Quick Reference Guide

> Use this guide to pick the right prompt template for the right task.
> All templates live in `chapter_02_Prompt_Engineering/Prompt_Template/` organized into 3 categories.

---

## How to Use This Guide

1. Identify the **type of work** you are doing: writing test cases, testing an API, or handling bugs.
2. Find your **category** below and match the task to a template.
3. Copy the template `.txt` file content, fill in the placeholders (`[PASTE ...]`, `[FEATURE]`, `[MODULE]`), and paste the required documentation.
4. If unsure, start with the **"Best for" / "Use when"** column — it describes the scenario each template fits.

---

## 1. Basic Test Case Prompts

*Folder: `BasicTestCasePrompts/`*

| Template File | Template Name | Best For / Use When | Key Output |
|---|---|---|---|
| `BasicTestCaseGeneration.txt` | Template 1: Basic Test Case Generation (RTCFR) | General feature-level test cases from requirements (SRS, Jira, ticket). Simple, quick functional coverage. | `\| Test ID \| Description \| Pre-conditions \| Steps \| Expected Result \| Priority \|` |
| `PRDToTestCaseGeneration.txt` | Template 2: PRD to Test Cases (Comprehensive) | A full PRD / SRS / BRD / HLD / confluence page needs complete coverage (functional, negative, boundary, edge cases). | `\| TID \| Category \| Description \| Pre-conditions \| Steps \| Expected \| Priority \|` |
| `APITestCaseGeneration.txt` | Template 3: API Test Case Generation | Test cases for a specific API endpoint from API docs (happy path, invalid inputs, auth, error handling, boundaries). | `\| Test ID \| Endpoint \| Method \| Request Body \| Expected Status \| Expected Response \|` |
| `NegativeTestCaseOnly.txt` | Template 4: Negative Test Cases Only | You only want negative/error-path scenarios (invalid inputs, boundary violations, missing fields, unauthorized access). | `\| Test ID \| Invalid Scenario \| Input \| Expected Error \|` |
| `RegressionTestSuite.txt` | Template 6: Regression Test Suite | Building a regression suite for a module before release — end-to-end flows, data setup, priorities, time estimates. | `\| Test ID \| Scenario \| Data Setup \| Steps \| Est. Time \| Priority \|` |

---

## 2. API Testing Prompts

*Folder: `APITestingPrompts/`*

| Template File | Template Name | Best For / Use When | Key Output |
|---|---|---|---|
| `RestAPITestSuite.txt` | Template 1: REST API Test Suite | A full comprehensive suite for a REST endpoint — happy path, validation, auth, HTTP methods, response validation, error handling. | `\| Test ID \| Category \| Method \| Endpoint \| Request \| Expected Status \| Expected Response \|` |
| `APIValidationTest.txt` | Template 2: API Validation Tests | Input validation focus — missing fields, wrong types, boundary values, invalid formats, special chars, empty vs null. | `\| Test ID \| Field \| Invalid Input \| Expected Error Code \| Expected Message \|` |
| `APIAuthenticationTest.txt` | Template 3: API Authentication Tests | Security-focused — no/invalid/expired token, permissions, token tampering, rate limiting. | `\| Test ID \| Auth Scenario \| Request Setup \| Expected Status \| Security Validation \|` |
| `APIContractTestng.txt` | Template 4: API Contract Testing | Validate response structure against a schema/OpenAPI spec — required fields, types, nullables, array bounds. | `\| Test ID \| Response Type \| Field \| Expected Type \| Required \| Validation \|` |
| `APIPerformaceTestScenario.txt` | Template 5: API Performance Test Scenarios | Design perf scenarios — baseline, load, stress, spike, endurance — with users, duration, ramp-up, pass criteria. | `\| Scenario \| Users \| Duration \| Ramp-up \| Pass Criteria \|` |
| `APIErrorHandlingTest.txt` | Template 6: API Error Handling Tests | Error handling focus — 4xx/5xx, timeouts, malformed requests, service unavailable, safe error messages. | `\| Test ID \| Error Scenario \| Trigger \| Expected Code \| Expected Response Format \|` |

---

## 3. Bugs Related Prompts

*Folder: `BugsRelatedPrompts/`*

| Template File | Template Name | Best For / Use When | Key Output |
|---|---|---|---|
| `BugReportFromEvidence.txt` | Template 1: Basic Bug Report from Evidence | You have screenshots/logs and need a structured bug report strictly from that evidence. | `Title / Environment / Severity / Steps to Reproduce / Expected Result / Actual Result / Evidence` |
| `BugClassification.txt` | Template 2: Bug Classification | Classify a bug's severity (Critical/High/Medium/Low) and priority based only on the description. | `Severity / Priority / Justification / Missing Information` |
| `BugAnalysisChainOfThoughts.txt` | Template 3: Bug Analysis (Chain-of-Thought) | Deep-dive root-cause analysis — symptoms, verified facts, gaps, possible causes, next steps. | `Step 1-5 analysis with facts vs hypotheses` |
| `ConvertToBugFromNotes.txt` | Template 5: Convert Notes to Bug Report | Informal/rough notes need to become a formal, structured bug report. | Formal bug report with `[NEEDS CLARIFICATION]` gaps |

---

## Quick Decision Matrix

| Situation | Category | Template to Use |
|---|---|---|
| Feature test cases from requirements | Basic | Basic Test Case Generation |
| Comprehensive coverage from a PRD | Basic | PRD to Test Cases |
| Test cases for one API endpoint | Basic / API | API Test Case Generation |
| Only negative scenarios | Basic | Negative Test Cases Only |
| Full REST API suite | API | REST API Test Suite |
| Input validation only | API | API Validation Tests |
| Auth/security tests | API | API Authentication Tests |
| Response schema/contract checks | API | API Contract Testing |
| Performance/load scenarios | API | API Performance Test Scenarios |
| Error handling / 4xx-5xx | API | API Error Handling Tests |
| Regression before release | Basic | Regression Test Suite |
| Bug report from screenshots/logs | Bugs | Bug Report from Evidence |
| Classify severity & priority | Bugs | Bug Classification |
| Root-cause analysis | Bugs | Bug Analysis (Chain-of-Thought) |
| Turn notes into formal bug report | Bugs | Convert Notes to Bug Report |

---

*Note: Template numbers restart per category (each folder numbers its own templates 1-6 / 1-5). Reference templates by their file name to avoid ambiguity.*
