# 05 — Screenshot to Bug Reporter (Plan)

> Upload a screenshot of a bug. AI writes the full bug report. n8n files it in Jira with the screenshot attached.

Workflow file: [`05_ScreenshotToBugReporter.json`](./05_ScreenshotToBugReporter.json)

---

## 1. The Problem

Filing bugs by hand is slow, and every tester writes them differently.

| Input | Output |
|---|---|
| A UI screenshot, plus optional error logs and notes | A Jira **Bug** with summary, steps to reproduce, expected and actual results, visual details, environment, severity and the screenshot attached |

**Who it helps:** testers who want to file a bug fast without typing out every visual detail.

---

## 2. Which Model? (Research)

We need a **vision** model, meaning one that can "see" images. We looked at Groq and OpenRouter.

Prices are in USD per **1 million tokens**, checked on **3 Oct 2026** from the OpenRouter models API and the Groq docs.

| Model | Where | Input | Output | Notes |
|---|---|---|---|---|
| `qwen/qwen3.8-27b:free` **(chosen)** | OpenRouter | $0 | $0 | Reads images and supports structured output. Rate limited (about 20 requests/min; 50/day with no credits, 1000/day after buying ≥ $10 credits). Free providers may log your prompts. |
| `google/gemini-2.5-flash-lite` **(fallback)** | OpenRouter | $0.10 | $0.40 | About **$0.0006 per bug**. Very good at reading text on screen. |
| `meta-llama/llama-4-scout` | OpenRouter | $0.10 | $0.30 | Cheap, but weaker at reading small UI text |
| `openai/gpt-5-nano` | OpenRouter | $0.05 | $0.40 | Hidden "reasoning" tokens push the real cost up |
| `qwen/qwen3.8-27b` (paid) | OpenRouter | $0.42 | $3.00 | Same model as the free one, without the limits |
| `qwen/qwen3.8-27b` | Groq | $0.80 | $4.00 | The **only** vision model on Groq. Very fast (about 450 tokens/sec) and has a free tier. Max 3 images and 20 MB per image. |
| `openai/gpt-5-mini` (what workflows 01, 02 and 04 use) | OpenAI | $0.25 | $2.00 | Our current baseline |

### What we decided

- **Groq** is the fastest, but it has only one vision model and is **not** the cheapest on paid use.
- **OpenRouter free Qwen** costs **$0**. It is good for learning and demos.
- **Gemini 2.5 Flash Lite** is the cheapest *reliable* paid choice. We wired it in as an automatic **fallback**: if the free model fails or is rate limited, n8n uses Gemini instead.

> **Careful:** free models can log your prompts. Do not upload screenshots that show passwords, customer data or secrets. For real company bugs, switch to a paid model (see section 7).

> **Tip:** to use Groq instead, swap the *OpenRouter Vision Model* node for a **Groq Chat Model** node with model `qwen/qwen3.8-27b`.

---

## 3. How the Workflow Looks

```text
Upload Screenshot (Form)
   ↓
Normalize Input (Code)
   ↓
Analyze Screenshot (Basic LLM Chain)  ← OpenRouter Vision Model (free Qwen)
   │                                  ← Fallback Vision Model (Gemini Flash Lite)
   │                                  ← Bug Report Parser (Structured Output)
   ↓
Build Jira Description (Code)
   ↓
Create Bug (Jira)
   ↓
Prepare Attachment (Code)
   ↓
Attach Screenshot (Jira)
   ↓
Show Result (Form Ending)
```

**Why a Form and not a Webhook?** The spec asked for a webhook. A **Form Trigger** gives testers a real upload page in the browser, so nobody needs Postman or curl.

---

## 4. Node by Node

| # | Node | Type | What it does |
|---|---|---|---|
| 1 | **Upload Screenshot** | Form Trigger | A web form with 4 fields: **Screenshot** (required, png/jpg/webp), *What were you doing?*, *Environment / Page URL*, *Error Logs* |
| 2 | **Normalize Input** | Code | Checks that the file is an image, renames it to `screenshot` and cleans up the text fields |
| 3 | **Analyze Screenshot** | Basic LLM Chain | Sends a QA-engineer system prompt, the tester's text and the **image** (as an "Image (Binary)" message) to the model. Retries 3 times if it fails. |
| 3a | **OpenRouter Vision Model** | OpenRouter Chat Model | `qwen/qwen3.8-27b:free`, temperature 0.2 (low = consistent reports) |
| 3b | **Fallback Vision Model** | OpenRouter Chat Model | `google/gemini-2.5-flash-lite`, used only if 3a fails |
| 3c | **Bug Report Parser** | Structured Output Parser | Forces the AI to answer in a fixed JSON shape (see below) |
| 4 | **Build Jira Description** | Code | Turns the JSON into Jira formatting: headings, numbered steps, bullet lists and a `{code}` block for logs (cut at 10,000 characters). Maps priority names to Jira IDs and cleans the labels. |
| 5 | **Create Bug** | Jira | Creates a **Bug** in the **AwesomeQA** project with summary, description, priority and labels (`ai-generated`, `screenshot-bug` + AI labels) |
| 6 | **Prepare Attachment** | Code | The Jira node drops the image, so this node brings the screenshot back and builds the ticket link |
| 7 | **Attach Screenshot** | Jira (Issue Attachment → Add) | Uploads the screenshot to the new ticket |
| 8 | **Show Result** | Form (Completion) | Shows the tester "Bug KAN-12 created" with a link |

### The JSON the AI must return

```json
{
  "summary": "[Login] Submit button shows error for valid user",
  "description": "Short paragraph about the bug",
  "steps_to_reproduce": ["Open /login", "Enter valid email and password", "Click Submit"],
  "expected_result": "User lands on the dashboard",
  "actual_result": "Red banner 'Something went wrong' appears",
  "severity": "Critical | Major | Minor | Trivial",
  "priority": "Highest | High | Medium | Low | Lowest",
  "environment": { "browser": "Chrome", "os": "Unknown", "url": "https://...", "app_version": "Unknown" },
  "visual_observations": ["Banner overlaps the header", "Button text cut off"],
  "error_summary": "TypeError in login.js line 42",
  "labels": ["login", "ui"]
}
```

---

## 5. One-Time Setup

1. In n8n, go to **Workflows → Import from File** and pick `05_ScreenshotToBugReporter.json`.
2. Create an **OpenRouter** credential:
   - Get a key at <https://openrouter.ai/keys>.
   - In n8n: **Credentials → New → OpenRouter**. Paste the key.
   - Select this credential in **both** model nodes.
3. For free models, open OpenRouter **Settings → Privacy** and allow free model endpoints. Otherwise free models return a 404.
4. Open **Create Bug** and **Attach Screenshot**, then re-select your **Jira SW Cloud account** credential.
5. **Create Bug** already uses **Issue Type → Bug** (ID `10043` in AwesomeQA). You only need to change it if you point the workflow at a different project.
6. Save the workflow.

---

## 6. How to Test

1. Click **Execute workflow**. The form opens on its **test URL**.
2. Upload a screenshot of a broken page, for example a login page with an error banner. Paste a few lines of console error.
3. Submit, then check the following:
   - The result page shows the ticket key and link.
   - In Jira the bug has: a clear summary, numbered steps, expected and actual results, a visual observations list, an environment section, the logs in a code block, labels, a priority and **the screenshot attached**.
4. Test again with **only** the screenshot (all optional fields empty). It must still work.
5. When you are happy, **Activate** the workflow and share the **production URL** of the form with your testers.

---

## 7. Troubleshooting and Costs

| Problem | Fix |
|---|---|
| `429 Too Many Requests` from the free model | The fallback (Gemini) takes over automatically if your OpenRouter account has credits. Otherwise wait a minute, or buy $10 of credits to raise the daily limit. |
| `404 No endpoints found` for the free model | Allow free endpoints in OpenRouter privacy settings (setup step 3). |
| "Could not parse output" | Free models sometimes break the JSON format. The node retries 3 times. If it keeps failing, make Gemini the main model. |
| Jira says "Field 'priority' cannot be set" | Your project's Bug screen has no Priority field. Remove *Priority* from **Create Bug → Additional Fields**. |
| Jira priority is wrong | The workflow uses the default Jira Cloud IDs (1 = Highest … 5 = Lowest). If your site uses custom priorities, change the `PRIORITY_IDS` map in **Build Jira Description**. |
| "The uploaded file is not an image" | Upload a png, jpg or webp file. |

### Switching to a paid model (for real company bugs)

Open **OpenRouter Vision Model** and change the model to `google/gemini-2.5-flash-lite`. That is the only change needed.

**Cost per bug:** one screenshot is about 1,500–2,500 tokens in and about 800 tokens out.
- Gemini Flash Lite: about **$0.0006** per bug (about 1,600 bugs per $1).
- gpt-5-mini: about **$0.002** per bug.

---

## 8. Vercel Production UI Plan

Added on **2026-10-03 13:48 IST**.

Goal: replace the public-facing n8n form page with a polished Vercel-hosted UI that shows no n8n URL, branding or implementation detail to testers.

### Implementation Plan

1. Create a dedicated Next.js app inside this chapter folder for the Screenshot Bug Reporter UI.
2. Build a classy tester-facing upload experience with:
   - screenshot upload with drag-and-drop styling,
   - notes, environment/page URL and error log fields,
   - progress, validation, success and failure states,
   - no visible n8n wording or n8n URLs.
3. Add a server-side API route at `/api/report-bug` so the browser never calls the automation URL directly.
4. Store the automation endpoint in a Vercel environment variable named `N8N_BUG_REPORTER_URL`.
5. Forward the uploaded screenshot and form fields from the API route to the production automation endpoint using multipart form data.
6. Keep deployment ready with `package.json` scripts, `vercel.json`, `.env.example`, TypeScript config and a short README.
7. Verify locally with lint/build so the app can be deployed quickly to Vercel when requested.

### Production Notes

- The deployed site should only expose the Vercel domain/custom domain and `/api/report-bug`.
- The n8n form URL must stay server-side in Vercel project settings.
- The UI copy should describe the product as an AI bug reporter, not as an n8n workflow.
- Vercel Functions currently cap request and response payloads at 4.5 MB, so the UI should optimize large screenshots before submission and the API proxy should reject any oversized forwarded payload.

---

## 9. UI Overlap Fix Plan

Added on **2026-10-03 13:59 IST**.

Issue: on wide desktop viewports, the large "Screenshot Bug Reporter" heading can overflow the left column and visually run underneath the upload form panel.

Plan:

1. Reduce the desktop headline maximum size and viewport scaling.
2. Increase the desktop grid gap and give both grid columns `min-width: 0`.
3. Keep the form panel above normal flow without covering title text.
4. Add a mid-width breakpoint so the page switches to a single-column layout before the heading and form can collide.
5. Re-run validation and preview checks.

---

## 10. Local Submit Fix Plan

Added on **2026-10-03 14:05 IST**.

Issue: the Python static preview server can serve the UI, but it returns `501 Unsupported method` for `POST /api/report-bug`, so bug creation fails locally.

Plan:

1. Add a small Node local server that serves the static UI and implements `POST /api/report-bug`.
2. Reuse the same server-side forwarding behavior as the Vercel API route.
3. Load `N8N_BUG_REPORTER_URL` from a local ignored env file for development.
4. Update scripts and README so local testing uses the Node server, not the static Python server.
5. Start the correct local server and verify `/api/report-bug` no longer returns the static-server `501`.

---

## 11. Ticket Return and Creation Verification Plan

Added on **2026-10-03 14:10 IST**.

Issue: the UI currently shows a generic success message after submission and does not expose the Jira ticket key created by the automation.

Plan:

1. Update the server-side proxy to inspect the automation completion response.
2. Extract the Jira ticket key and ticket URL from the response when present.
3. Return `{ ok, ticketKey, ticketUrl, message }` from `/api/report-bug`.
4. Update the UI success state to show the created ticket number and open link.
5. Submit a local test report through the proxy and confirm a real ticket key is returned.

### Async Status Adjustment

The live workflow can run longer than one request should wait, so `/api/report-bug` will return a private status token when n8n reports a waiting execution. The UI will poll `/api/report-status` until the workflow returns a Jira ticket key, fails, or times out.

---

## 12. Final Vercel UI Deployment Readiness Plan

Added on **2026-10-03 14:31 IST**.

Goal: expose the production bug reporter through a Vercel-hosted UI with no n8n branding, visible n8n URL, or implementation traces on the tester-facing page.

Plan:

1. Use the production automation form URL only as a server-side environment variable named `N8N_BUG_REPORTER_URL`.
2. Keep the browser posting only to first-party Vercel routes:
   - `/api/report-bug` to submit the screenshot and notes.
   - `/api/report-status` to poll slow LLM/Jira execution status.
3. Wait for long-running workflow completion by returning a private encrypted status token and polling for up to 12 minutes from the browser.
4. Parse the final workflow completion response and require a Jira-style ticket key such as `KAN-12` before showing success.
5. Show the created ticket number prominently, include the Jira URL, add a **Copy URL** button, and add a **Log another bug** button that resets the form.
6. Keep all visible UI copy provider-neutral and polished.
7. Verify that browser-facing files contain no n8n URL/traces, validate the code, and run the local server for quick manual testing.

---

## 13. Vercel Production Deployment Plan

Added on **2026-10-03 14:56 IST**.

Goal: deploy the custom Screenshot Bug Reporter UI to Vercel production using the logged-in Vercel account, while keeping the automation URL hidden server-side.

Plan:

1. Confirm the local app validates with `npm run build`.
2. Link/create a Vercel project from `screenshot-bug-reporter-ui`.
3. Add production environment variables:
   - `N8N_BUG_REPORTER_URL`
   - `STATUS_TOKEN_SECRET`
4. Deploy to Vercel production.
5. Return the production URL and any deployment caveats.

---

## 14. Vercel Automatic Deployment Gate Plan

Added on **2026-10-03 15:04 IST**.

Goal: make Git-triggered Vercel production deployments run only when a push to the `main` branch changes `chapter_08_n8n_Agents/05_ScreenshotToBugReporter.json`.

Plan:

1. Add a repository script that Vercel can run as its Ignored Build Step.
2. The script will:
   - allow deployment only when `VERCEL_GIT_COMMIT_REF` is `main`,
   - check the changed files for the current commit/range,
   - proceed only when `chapter_08_n8n_Agents/05_ScreenshotToBugReporter.json` changed,
   - ignore deployment for all other branches or file changes.
3. Configure the Vercel project to use that ignore command.
4. Confirm the project remains public and production env vars stay configured.
5. Validate the script locally with representative branch/file-change scenarios.
