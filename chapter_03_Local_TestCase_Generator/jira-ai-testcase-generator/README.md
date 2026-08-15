# Jira AI Test Case Generator

A local, AI-powered QA assistant that turns a Jira ticket into structured test cases.

You type something like **"Create test cases for ABC-123"** — the app extracts the Jira ID,
fetches the ticket from Jira, reads your test case template, and generates test cases using
your **local Ollama model (Gemma 3 4B)**, with **Groq** as an alternative or fallback provider.

Built with Python + Streamlit. Everything runs locally.

---

## Features

- **Two-page Streamlit app** — Chat/Test Case Generator + Settings/Configuration.
- **Jira REST API integration** — automatic ticket fetch with safe handling of missing fields.
- **Natural-language Jira ID extraction** — no separate ID field needed.
- **Local-first AI** — uses your existing Ollama installation (Gemma 3 4B).
- **Groq support** — selectable provider, plus automatic Ollama → Groq fallback when Ollama is down and a key is set.
- **External template** — output format is driven by `templates/test_case_template.md` (the source of truth).
- **Secure configuration** — credentials are read from local `.env`; secrets are masked in the UI and never logged.
- **Connection testing** — one-click checks for Jira, Ollama, and Groq on the Settings page.

---

## Architecture

```
User prompt
   │  "Create test cases for ABC-123"
   ▼
Extract Jira ID ───────────────► jira_parser.py (regex)
   ▼
Fetch Jira ticket ─────────────► services/jira_service.py (Jira REST API)
   ▼
Parse requirements ────────────► utils/jira_parser.py (tolerant field extraction)
   ▼
Load test case template ───────► utils/template_loader.py
   ▼
Build AI prompt ───────────────► utils/prompt_builder.py
   ▼
Generate test cases ───────────► services/llm_service.py
                                  ├── services/ollama_service.py  (local, default)
                                  └── services/groq_service.py    (alternative/fallback)
   ▼
Display result ────────────────► Streamlit (app.py)
```

The LLM provider layer is modular: `llm_service.generate_response(prompt, config)` dispatches
to Ollama or Groq without coupling the test-generation logic to either provider, so new
providers can be added later without rewriting the rest of the app.

---

## Folder Structure

```
jira-ai-testcase-generator/
├── app.py                      # Page 1 — Chat / Test Case Generator (entry point)
├── pages/
│   └── settings.py             # Page 2 — Settings / Configuration + connection tests
├── services/
│   ├── __init__.py
│   ├── jira_service.py         # Jira REST API only
│   ├── ollama_service.py       # Ollama API only
│   ├── groq_service.py         # Groq API only
│   └── llm_service.py          # Provider dispatch + fallback
├── utils/
│   ├── __init__.py
│   ├── config_manager.py       # .env load/save + secret masking
│   ├── jira_parser.py          # issue JSON → requirement context
│   ├── prompt_builder.py       # LLM prompt assembly
│   └── template_loader.py      # template file loading
├── templates/
│   └── test_case_template.md   # source of truth for the output format
├── config/
│   └── .gitkeep
├── .env.example                # placeholder config template only
├── .env                        # local config; do not commit real credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python 3.10+**
- **Ollama** installed and running locally with the Gemma 3 4B model pulled.
- A **Jira** account with an API token (Atlassian: https://id.atlassian.com/manage-profile/security/api-tokens).
- Optional: a **Groq** API key (https://console.groq.com) for the alternative provider.

### Verify Ollama

```bash
ollama list          # confirm "gemma3:4b" is present
curl http://localhost:11434/api/tags
```

If the model is missing, pull it once:

```bash
ollama pull gemma3:4b
```

---

## Setup and Run

### 1. Clone / open the project

```bash
cd chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

| Variable | Description |
|---|---|
| `JIRA_BASE_URL` | Your Jira site, e.g. `https://your-domain.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email |
| `JIRA_API_TOKEN` | Jira API token (not your password) |
| `OLLAMA_BASE_URL` | Usually `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model used by the app: `gemma3:4b` |
| `GROQ_API_KEY` | Groq API key (optional unless you use Groq) |
| `GROQ_MODEL` | Groq model, e.g. `llama-3.3-70b-versatile` |
| `AI_PROVIDER` | `ollama` (default) or `groq` |
| `ACCEPTANCE_CRITERIA_FIELD_ID` | Optional: Jira custom field holding acceptance criteria |

Keep `.env` local and never commit real credentials. Treat `.env.example` as a placeholder file only.

### 5. Make sure Ollama is running

If you are using the default `ollama` provider, Ollama must be available before generation starts.

```bash
ollama list
ollama pull gemma3:4b        # run only if the model is missing
ollama serve                 # run only if Ollama is not already running
```

If you prefer Groq, set `AI_PROVIDER=groq` and provide `GROQ_API_KEY`.

### 6. Start the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`).

---

## Guide: Run the App and Generate Test Cases

Follow this flow when you want to generate test cases from a Jira ticket.

### Step 1 - Start Streamlit

From the app folder, activate your virtual environment and start the app:

```bash
cd chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator
source venv/bin/activate
streamlit run app.py
```

On Windows:

```bash
cd chapter_03_Local_TestCase_Generator\jira-ai-testcase-generator
venv\Scripts\activate
streamlit run app.py
```

Streamlit opens in the browser. If it does not open automatically, copy the local URL from the terminal, usually:

```text
http://localhost:8501
```

### Step 2 - Configure Jira and AI provider

Open the **Settings** page from the Streamlit sidebar.

Fill in the required Jira values:

- `JIRA_BASE_URL`, for example `https://your-domain.atlassian.net`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Fill in the AI provider values:

- For local Ollama: `OLLAMA_BASE_URL=http://localhost:11434`, `OLLAMA_MODEL=gemma3:4b`, `AI_PROVIDER=ollama`
- For Groq: add `GROQ_API_KEY`, set `GROQ_MODEL`, and choose `AI_PROVIDER=groq`

Click **Save Configuration**.

### Step 3 - Test connections

Still on the **Settings** page, click:

- **Test Jira Connection**
- **Test Ollama Connection** if using Ollama
- **Test Groq Connection** if using Groq

Fix any failed connection before generating test cases. The most common issues are an incorrect Jira token, Ollama not running, or a model name that does not match `ollama list`.

### Step 4 - Generate test cases

Go back to the **Chat / Test Case Generator** page.

Enter a request that contains a Jira issue key:

```text
Create test cases for PROJ-123
```

You can also ask for a test plan:

```text
Generate a test plan for QA-456
```

Click **Send**.

The app will:

1. Extract the Jira key from your request.
2. Fetch the ticket from Jira.
3. Parse summary, description, acceptance criteria, priority, labels, components, and supported custom fields.
4. Load `templates/test_case_template.md`.
5. Build the AI prompt using the Jira requirements and template.
6. Generate test cases with Ollama or Groq.
7. Display the result in the browser.

### Step 5 - Adjust the output format if needed

To change the generated test-case structure, edit:

```text
templates/test_case_template.md
```

The app reloads this template on every request, so you do not need to restart Streamlit after changing the template.

---

## How to Use

### Chat / Test Case Generator (Page 1)

1. Enter a natural-language request, e.g.:
   - `Create test cases for ABC-123`
   - `Generate a test plan for QA-456`
2. Click **Send**.
3. Watch the progress: *Fetching Jira requirements... → Loading test case template... → Generating test cases...*
4. The generated test cases appear below, following your template.

The app extracts the Jira ID automatically. If it cannot find one, it shows a clear message.

### Settings / Configuration (Page 2)

1. Fill in Jira, Ollama, and Groq settings.
2. Choose the primary AI provider (**Ollama** or **Groq**).
3. Click **Save Configuration** — values are written to `.env`.
4. Use **Test Jira / Ollama / Groq Connection** to verify each service.
5. Secret fields (Jira token, Groq key) are masked — leave them blank to keep the saved value.

**Provider fallback:** when `AI_PROVIDER=ollama` and Ollama is unreachable, the app automatically
tries Groq if a `GROQ_API_KEY` is configured. The response notes which provider was used.

---

## Templates

- The output format is defined entirely by `templates/test_case_template.md`.
- Edit that file to change how test cases are structured — no code changes needed.
- The template is loaded from disk on every request, so edits take effect immediately.
- Missing template? The app shows a clear error instead of crashing.

Example template format (the one shipped with this project):

```markdown
| Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |
|---------|-------------|----------------|-------|-----------------|----------|
```

---

## Security

- **Never hardcoded** — Jira token and Groq key are read from `.env` only.
- **Keep `.env` local** — credentials should never reach the repository.
- **Use placeholders only** — `.env.example` should contain sample values, not real tokens.
- **Masked in the UI** — secrets show only a masked hint (`sk-abc...1234`).
- **Not logged** — no logger prints tokens, keys, or authorization headers.
- **Safe error messages** — exceptions shown to users never include credentials.
- If you use the Groq key or Jira token in any external tool, rotate them if they are ever exposed.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Unable to reach Ollama` | Start Ollama: `ollama serve` (or the desktop app), then re-test. |
| `model 'gemma3:4b' is not installed` | Run `ollama list`, then set `OLLAMA_MODEL` to the exact tag shown, or `ollama pull gemma3:4b`. |
| `Jira authentication failed` | Check `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.env`; generate a token at Atlassian API tokens. |
| `Jira issue X was not found` | Confirm the project key and that your account can see the ticket. |
| `Groq authentication failed` | Check `GROQ_API_KEY`; verify it is active at https://console.groq.com. |
| `Groq model not available` | Set `GROQ_MODEL` to a model listed at https://console.groq.com/docs/models. |
| `Could not identify a Jira ticket ID` | Include a ticket key like `PROJ-123` in your request. |
| Generation is slow on Ollama | Gemma 3 4B can take time on CPU; give it a moment. Reduce ticket size or use Groq. |
| Settings don't seem to save | Confirm the app has write access to the project `.env`; check for console errors. |

---

## Validation Checklist

- [ ] App starts with `streamlit run app.py`; both pages load.
- [ ] Jira connection test passes with your credentials.
- [ ] Ollama connection test passes; model tag matches `OLLAMA_MODEL`.
- [ ] Entering `Create test cases for <KEY>` fetches the ticket and generates test cases.
- [ ] Invalid Jira ID / missing template / empty prompt show friendly errors.
- [ ] Secrets are not visible in the UI, logs, or `git status`.
