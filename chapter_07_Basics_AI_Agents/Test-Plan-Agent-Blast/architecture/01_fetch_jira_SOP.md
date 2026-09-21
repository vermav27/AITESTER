# SOP 01 — Fetch a Jira ticket

**Layer:** L3 tool (`core/jira_client.py`, CLI `tools/fetch_jira.py`)
**Golden rule:** if this logic changes, update this SOP before the code.

## Goal

Retrieve the raw JSON for exactly one Jira issue, plus its comments, without ever
mutating the ticket. This is the only place in the project that talks to Jira.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `KEY` | the user's prompt, validated by `navigation.extract_jira_key` | regex `^[A-Z][A-Z0-9]{1,9}-\d{1,6}$` |
| `JIRA_BASE_URL` | `.env` / Settings page | no trailing slash required |
| `JIRA_EMAIL` | `.env` / Settings page | present ⇒ Basic auth |
| `JIRA_TOKEN` | `.env` / Settings page | absent email ⇒ Bearer auth (Server/DC) |

## Requests used

```
GET  {base}/rest/api/3/issue/{KEY}?fields=summary,description,issuetype,priority,
     status,components,labels,fixVersions,issuelinks,attachment,comment,created,updated
GET  {base}/rest/api/3/issue/{KEY}/comment?maxResults=100&orderBy=created
GET  {base}/rest/api/3/myself                                  # connection test
GET  {base}/rest/api/3/project/search?maxResults=100           # project validation
POST {base}/rest/api/3/search/jql                              # latest ticket in a project
```

`POST /search/jql` body: `{"jql": "project = \"KAN\" ORDER BY created DESC", "maxResults": 1, "fields": [...]}`.

**Never** use `GET /rest/api/3/search` — it is deprecated and returns HTTP 410 on this
instance. The API v2 family is also gone.

## Tool logic

1. Validate the base URL and token are present; otherwise raise `JiraError` immediately (no request).
2. Send the request with a 20 s timeout and `Accept: application/json`.
3. On connection error / timeout / 429 / 5xx: retry up to 3 attempts with backoff,
   honouring `Retry-After` on 429 (capped at 10 s).
4. On 4xx: raise `JiraError` with a message from the status map below and stop.

## Edge cases

| Case | Behaviour |
|---|---|
| 400 | invalid JQL/field list — show the request, stop |
| 401 | token wrong or expired — say so explicitly, hint at regenerating the token |
| 403 | no permission to the project/issue — name the key |
| 404 | ticket not found — exit non-zero, never fabricate |
| 410 | legacy endpoint removed — the agent targets API v3 |
| 429 / 5xx | bounded retry, then surface the error |
| Empty body | return `{}` rather than crashing the JSON parse |

## Invariants

- Read-only. No transitions, comments, or edits — ever.
- A failed fetch must never degrade into an empty or invented plan (rule R9).
- Tokens and authorization headers never appear in a message, artifact, or log (rule R4).
