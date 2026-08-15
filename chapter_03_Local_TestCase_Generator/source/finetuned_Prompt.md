# RICEPOT FRAMEWORK

## R — ROLE

1. You are a **Senior Python Developer, AI Application Engineer, and QA Automation Architect with 15+ years of experience** in software development, testing, REST API integrations, and AI-powered applications.

2. You have strong expertise in:

   * Python
   * Streamlit
   * REST APIs
   * Jira REST API
   * Ollama
   * Local LLM integration
   * Gemma 3
   * Groq API
   * Prompt Engineering
   * Software Testing
   * Test Case Design
   * Test Plan Creation
   * JSON processing
   * Secure credential/configuration management

3. You have a strong understanding of QA activities such as:

   * Requirement analysis
   * Jira story analysis
   * Acceptance criteria analysis
   * Functional test case generation
   * Positive test scenarios
   * Negative test scenarios
   * Boundary test scenarios
   * Validation scenarios
   * Test planning

4. Act as an experienced engineer who follows:

   * Clean Code principles
   * Modular architecture
   * Security best practices
   * Reusable design
   * Proper exception handling
   * Maintainable project structure
   * Production-quality coding standards

5. Your primary objective is to build a **simple AI-powered Jira Test Case Generator application** using Python.

6. The application should allow a user to enter a natural-language request such as:

   **"Create test cases for Jira ticket ABC-123."**

   The application should:

   * Identify the Jira ticket.
   * Fetch its details automatically from Jira.
   * Read the required test case format/template.
   * Send the Jira requirements and template to an AI model.
   * Generate structured test cases.
   * Display the generated result to the user.

---

# I — INSTRUCTIONS

Build a complete working Python application according to the following requirements.

## 1. Application Overview

Create a simple **two-page Python application**.

Preferred frontend technology:

**Streamlit**

You may use another lightweight Python frontend framework only if there is a strong technical reason, but Streamlit should be the default choice.

The application should have the following pages:

1. **Chat / Test Case Generator**
2. **Settings / Configuration**

The application should be easy to run locally.

---

# 2. PAGE 1 — CHAT / TEST CASE GENERATOR

Create a frontend experience similar to a basic ChatGPT interface.

The user should have:

* A text input/chat input field.
* A Send button.
* An area where generated output is displayed.

Example user request:

> Create test cases for Jira ticket ABC-123.

Another example:

> Generate a test plan for QA-456.

The system should understand the Jira ID from the user's request.

---

# 3. JIRA TICKET IDENTIFICATION

When the user submits a prompt, identify the Jira ticket ID from the request.

Example:

User:

> Create test cases for PROJ-123.

Extract:

```text
PROJ-123
```

Do not require the user to manually enter the Jira ID separately if it can be identified from the prompt.

If a valid Jira ticket ID cannot be identified, display a clear message to the user instead of crashing.

---

# 4. JIRA INTEGRATION

Use the **Jira REST API** to retrieve the details of the Jira ticket.

The following configuration values will be provided through the Settings page:

```text
Jira Base URL
Jira Email ID
Jira API Token
```

Example configuration:

```text
JIRA_BASE_URL = https://company.atlassian.net
JIRA_EMAIL = user@example.com
JIRA_API_TOKEN = <token>
```

Do NOT hardcode these values in the application source code.

---

# 5. JIRA DATA FETCHING

After extracting the Jira ID, automatically fetch the Jira issue details.

Where available, retrieve useful information such as:

* Jira ID
* Summary
* Description
* Acceptance Criteria
* Issue Type
* Priority
* Labels
* Components
* Relevant custom fields

However:

**Do not assume that every Jira ticket contains all these fields.**

If a field does not exist, handle it safely.

The application should not fail because an optional Jira field is unavailable.

---

# 6. REQUIREMENT PROCESSING

The Jira ticket details should be converted into clean structured requirement context before being sent to the AI model.

Example:

```text
Jira ID: ABC-123

Summary:
User should be able to log in.

Description:
The system should allow registered users to log in using email and password.

Acceptance Criteria:
1. Valid users can log in.
2. Invalid users receive an error.
3. Email should be validated.
```

Do not invent Jira requirements that are not present in the Jira ticket.

---

# 7. TEST CASE TEMPLATE

The project should contain a folder named:

```text
templates/
```

A test case template will be stored inside this folder.

For example:

```text
templates/
    test_case_template.md
```

The generated test cases MUST follow the structure defined inside this template.

Example template:

```text
| Test ID | Test Scenario | Pre-Condition | Test Steps | Test Data | Expected Result | Priority |
```

The template shown above is only an example.

The actual template file inside the `templates` folder must be considered the **source of truth**.

The application should dynamically read the template file instead of hardcoding its structure into the source code.

---

# 8. LOCAL AI MODEL — PRIMARY LLM

The PRIMARY AI model should be the locally running **Ollama** instance.

Ollama is already installed and running locally.

Use the locally available:

```text
Gemma 3 — 1 Billion Parameter Model
```

Use the locally installed Ollama model corresponding to Gemma 3 4B.

Do NOT attempt to download or reinstall the model if it already exists.

Connect to the existing local Ollama server.

Typical local Ollama connection may use:

```text
http://localhost:11434
```

However, keep the Ollama URL configurable rather than tightly hardcoding application logic around it.

---

# 9. GROQ — OPTIONAL/FALLBACK AI PROVIDER

The application should additionally support **Groq** as another AI provider.

The user should be able to configure a:

```text
Groq API Key
```

through the Settings page.

Do NOT hardcode the Groq API key.

Groq can be used in two ways:

### Option A — User Selection

Allow the user to select:

```text
AI Provider:

○ Ollama
○ Groq
```

OR

### Option B — Fallback

If Ollama is selected as the primary provider but the connection fails, the application may fall back to Groq **only if a valid Groq API key has been configured**.

The implementation should keep the AI provider layer modular so additional LLM providers can be introduced later without rewriting the entire application.

---

# 10. AI PROVIDER ABSTRACTION

Do NOT tightly couple test generation logic with Ollama.

Create a reusable architecture similar to:

```text
LLM Provider
     |
     +---- Ollama Provider
     |
     +---- Groq Provider
```

For example:

```python
generate_response(prompt, provider)
```

or equivalent modular implementation.

The same test generation prompt should work with either provider.

---

# 11. AI PROMPT GENERATION

Before calling the LLM, construct a structured prompt containing:

1. Role
2. Jira requirements
3. Jira acceptance criteria
4. Instructions
5. Test case template
6. Constraints

Example concept:

```text
ROLE:
You are a Senior QA Engineer.

TASK:
Generate comprehensive test cases based ONLY on the provided Jira requirements.

JIRA REQUIREMENTS:
{jira_content}

TEST CASE TEMPLATE:
{template_content}

CONSTRAINTS:
- Use only Jira requirements.
- Do not invent undocumented functionality.
- Cover positive and negative scenarios.
- Include boundary cases only where supported by requirements.
- If information is unavailable, state "Not specified".
- Follow the supplied template exactly.
```

The final prompt should be optimized so that the local **Gemma 3 4B** model can understand it reliably.

Avoid unnecessary tokens and overly complicated instructions.

---

# 12. PAGE 2 — SETTINGS / CONFIGURATION

Create a Settings page where the user can configure:

### Jira Configuration

```text
Jira Base URL
Jira Email ID
Jira API Token
```

### Ollama Configuration

```text
Ollama Base URL
Ollama Model Name
```

### Groq Configuration

```text
Groq API Key
Groq Model
```

### AI Provider

Allow selection between:

```text
Ollama
Groq
```

Provide a:

```text
Save Configuration
```

button.

---

# 13. SAVING CONFIGURATION

The configuration entered by the user should be reusable after saving.

Sensitive information such as:

```text
Jira API Token
Groq API Key
```

must NOT:

* Be hardcoded.
* Be committed to Git.
* Be printed in logs.
* Be displayed back to the user in plain text unnecessarily.
* Be exposed in exception messages.

Use an appropriate secure local configuration approach.

If a local configuration file is used, ensure that sensitive configuration files are included in:

```text
.gitignore
```

Provide an:

```text
.env.example
```

or equivalent example configuration containing only placeholder values.

---

# 14. CONNECTION TESTING

On the Settings page, where practical, provide:

```text
Test Jira Connection
Test Ollama Connection
Test Groq Connection
```

functionality.

Display meaningful results such as:

```text
✓ Jira connection successful
```

or:

```text
✗ Unable to connect to Jira.
```

Do not expose confidential authentication information inside error messages.

---

# 15. GENERATION WORKFLOW

The complete workflow should be:

```text
User enters prompt
        ↓
Extract Jira ID
        ↓
Load Jira configuration
        ↓
Connect to Jira
        ↓
Fetch Jira ticket
        ↓
Extract relevant requirements
        ↓
Load test case template
        ↓
Create AI prompt
        ↓
Determine selected AI provider
        ↓
Ollama / Groq
        ↓
Generate test cases
        ↓
Display result
```

---

# 16. LOADING INDICATOR

While Jira information is being fetched or test cases are being generated, show an appropriate frontend status such as:

```text
Fetching Jira requirements...
```

followed by:

```text
Generating test cases...
```

The UI should remain user-friendly.

---

# 17. ERROR HANDLING

Implement proper exception handling for at least:

* Invalid Jira ID
* Jira ticket not found
* Jira authentication failure
* Jira API unavailable
* Network issue
* Ollama unavailable
* Ollama model unavailable
* Groq API authentication failure
* Invalid Groq API key
* AI API failure
* Missing configuration
* Missing test template
* Invalid configuration file
* Empty user prompt

The application must not terminate unexpectedly because of these errors.

Display understandable error messages in the frontend.

---

# 18. SECURITY

[MANDATORY]

Never expose:

```text
Jira Token
Groq API Key
Passwords
Authorization headers
```

inside:

* Source code
* Console logs
* Application logs
* Frontend output
* Exception traces shown to users
* Git repository

Sensitive data should always be handled securely.

---

# 19. PROJECT ARCHITECTURE

Create a clean and maintainable folder structure.

A recommended architecture is:

```text
jira-ai-testcase-generator/
│
├── app.py
│
├── pages/
│   └── settings.py
│
├── services/
│   ├── jira_service.py
│   ├── ollama_service.py
│   ├── groq_service.py
│   └── llm_service.py
│
├── utils/
│   ├── config_manager.py
│   ├── jira_parser.py
│   ├── prompt_builder.py
│   └── template_loader.py
│
├── templates/
│   └── test_case_template.md
│
├── config/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

You may improve this structure if necessary, but do not create unnecessary architectural complexity.

---

# 20. MODULARITY

Follow separation of concerns.

For example:

```text
jira_service.py
```

should only handle Jira communication.

```text
ollama_service.py
```

should handle Ollama communication.

```text
groq_service.py
```

should handle Groq communication.

```text
prompt_builder.py
```

should construct the final LLM prompt.

```text
template_loader.py
```

should load the test case template.

Do not put the entire application logic inside `app.py`.

---

# 21. REQUIREMENTS FILE

Create:

```text
requirements.txt
```

containing all required Python packages.

Use stable and appropriate libraries.

Do not include unnecessary dependencies.

---

# 22. README

[MANDATORY]

Create a detailed:

```text
README.md
```

It should explain:

* Project objective
* Architecture
* Folder structure
* Prerequisites
* Python setup
* Virtual environment setup
* Dependency installation
* Ollama prerequisite
* Gemma 3 4B configuration
* Jira configuration
* Groq configuration
* How to start the application
* How to use the application
* How templates work
* Security considerations
* Troubleshooting

Include commands wherever necessary.

Example:

```bash
pip install -r requirements.txt
```

and:

```bash
streamlit run app.py
```

---

# 23. CODE QUALITY

The code should:

* Be readable.
* Be modular.
* Use meaningful names.
* Avoid duplicated logic.
* Include useful comments only where needed.
* Follow Python best practices.
* Follow PEP 8 wherever practical.
* Use reusable functions/classes.
* Implement proper exception handling.
* Avoid unnecessary complexity.

---

## DO

* Keep the application simple.
* Use Streamlit for the frontend.
* Use Jira REST API.
* Use Ollama as the primary local AI provider.
* Use the locally installed Gemma 3 4B model.
* Support Groq.
* Keep LLM providers modular.
* Use the external test case template.
* Generate test cases based on Jira information.
* Handle credentials securely.
* Include proper exception handling.
* Create a professional README.
* Make the project directly runnable.
* Follow clean architecture principles.
* Validate that the generated code actually works together.

---

## DON'T

* Do not hardcode Jira credentials.
* Do not hardcode Groq API keys.
* Do not expose tokens.
* Do not unnecessarily reinstall Ollama.
* Do not unnecessarily download Gemma if it already exists.
* Do not fabricate Jira information.
* Do not generate functionality unsupported by the Jira ticket.
* Do not hardcode the test case template.
* Do not tightly couple Ollama with business logic.
* Do not create unnecessary enterprise-level complexity for this simple application.
* Do not put all code in one Python file.
* Do not leave placeholder methods for important functionality.
* Do not provide pseudo-code where working implementation is expected.
* Do not ignore error scenarios.
* Do not silently hide important failures.

---

# C — CONTEXT

The objective is to create a **local AI-powered QA assistant** that generates test cases from Jira requirements.

Currently, QA engineers manually:

1. Open Jira.
2. Find a Jira story.
3. Read its requirements.
4. Read its acceptance criteria.
5. Analyze the requirements.
6. Prepare test cases.
7. Format those test cases according to the organization's test case template.

The new application should simplify this process.

A QA engineer should only need to enter something similar to:

> Create test cases for ABC-123.

The application should automatically retrieve the Jira ticket and generate the test cases.

The preferred AI model is a **locally running Ollama model** because most processing should be possible locally.

The locally available model is:

```text
Gemma 3 4B
```

Groq should be available as an alternative AI provider.

The application will initially run locally.

---

# E — EXAMPLE

## Example User Interaction

### User enters:

```text
Create test cases for LOGIN-101
```

### Application Processing

```text
Extract Jira ID:
LOGIN-101

↓

Fetch Jira ticket:
LOGIN-101

↓

Retrieve:
Summary
Description
Acceptance Criteria
Other relevant requirements

↓

Read:
templates/test_case_template.md

↓

Build LLM Prompt

↓

Send to:
Ollama → Gemma 3 4B

↓

Generate Test Cases
```

### Example Output

If the template contains:

```text
| Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |
```

the AI response could look similar to:

```text
| Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |
| TC-001 | Verify login using valid credentials | Valid registered account exists | 1. Open login page 2. Enter valid credentials 3. Click Login | User logs in successfully | High |
```

The exact output must depend entirely on:

1. Jira requirements.
2. The test case template.

---

# P — PARAMETERS

Use the following configurable parameters.

## Jira

```text
JIRA_BASE_URL = User configured
JIRA_EMAIL = User configured
JIRA_API_TOKEN = User configured
```

## Ollama

```text
OLLAMA_BASE_URL = Configurable
OLLAMA_MODEL = Locally installed Gemma 3 4B model
```

## Groq

```text
GROQ_API_KEY = User configured
GROQ_MODEL = User configured/default supported model
```

## Template

```text
templates/test_case_template.md
```

## Primary AI Provider

```text
Ollama
```

## Alternative Provider

```text
Groq
```

## Frontend

```text
Streamlit
```

## Backend

```text
Python
```

---

# O — OUTPUT

You are expected to **create the complete application**, not merely explain how it could be created.

Your final implementation should contain:

1. Complete project folder structure.
2. Working Streamlit frontend.
3. Chat/Test Case Generator page.
4. Settings page.
5. Jira REST API integration.
6. Jira ID extraction.
7. Jira requirement parsing.
8. Test case template loading.
9. Ollama integration.
10. Gemma 3 4B integration using the existing local Ollama installation.
11. Groq integration.
12. AI provider selection.
13. Optional Ollama → Groq fallback mechanism.
14. Secure configuration management.
15. Proper error handling.
16. Loading/progress indicators.
17. `requirements.txt`.
18. `.gitignore`.
19. `.env.example`.
20. `README.md`.
21. Clear setup instructions.
22. Clear execution instructions.

The completed application should be runnable using a simple command such as:

```bash
streamlit run app.py
```

---

# T — TONE

The implementation and documentation should be:

* Technical
* Professional
* Practical
* Clear
* Developer-friendly
* QA-engineer-friendly
* Easy for a new developer to understand

Avoid:

* Excessive theoretical explanation
* Generic recommendations
* Unnecessary architectural complexity
* Excessive abstraction
* Repetitive explanations
* Incomplete code
* Pseudo-code instead of actual implementation

---

# FINAL VALIDATION

Before considering the task complete, internally verify all of the following.

## Application

1. The Streamlit application starts successfully.
2. Both application pages are accessible.
3. The Chat/Test Generator page works.
4. The Settings page works.

## Jira

5. Jira configuration can be entered.
6. Jira credentials are not hardcoded.
7. Jira IDs can be extracted from natural-language prompts.
8. Jira tickets can be fetched using Jira REST API.
9. Invalid Jira IDs are handled properly.
10. Authentication failures are handled safely.

## Templates

11. The test case template is loaded from the `templates` folder.
12. The template is not unnecessarily hardcoded.
13. Generated test cases follow the supplied template.

## Ollama

14. The application connects to the existing Ollama installation.
15. The locally installed Gemma 3 4B model can be used.
16. Ollama connection failures are handled safely.

## Groq

17. Groq can be configured.
18. Groq API keys are handled securely.
19. Groq can be selected as an AI provider.
20. Groq failures are handled gracefully.

## Architecture

21. Jira logic is separated from UI logic.
22. Ollama logic is separated from UI logic.
23. Groq logic is separated from UI logic.
24. Prompt-building logic is modular.
25. Template-loading logic is modular.
26. Configuration management is modular.

## Security

27. Jira API Token is never exposed.
28. Groq API Key is never exposed.
29. Secrets are not committed to Git.
30. Secrets are not printed to logs.
31. Authorization headers are never exposed.

## Documentation

32. `requirements.txt` is complete.
33. `.gitignore` is correctly configured.
34. `.env.example` contains only safe placeholders.
35. `README.md` explains complete installation and usage.

## Code Quality

36. No important functionality is left as pseudo-code.
37. No unnecessary assumptions have been made.
38. No unnecessary complexity has been introduced.
39. All important exceptions are handled.
40. The complete flow works logically from:

```text
User Prompt
    ↓
Jira Ticket
    ↓
Requirements
    ↓
Template
    ↓
AI Model
    ↓
Generated Test Cases
```

41. The final application is practical and directly usable.

---

# FINAL EXECUTION INSTRUCTION

Now create the complete application according to the requirements above.

Do not only explain the implementation.

**Create the project, create all required files, write the complete working code, validate the integration between components, and ensure the application is ready to run locally.**
