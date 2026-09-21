"""L3 tool — Jira REST API v3 client.

Read-only against Jira (invariant I2 / rule R10): this module only ever issues
GET requests plus the single POST that Jira's search API requires. It never
transitions, comments on, or mutates an issue.

Auth (see ``findings.md`` §2):

* Atlassian Cloud → HTTP Basic with ``(email, API token)``.
* Server / Data Center → ``Authorization: Bearer <PAT>`` when no email is set.

Errors are raised as :class:`JiraError` carrying a structured payload and a
user-safe message. Credentials never appear in a message or a log line.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests

TIMEOUT_SECONDS = 20
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 1.5

# Fields requested for a test plan. Custom AC field is appended by the caller.
ISSUE_FIELDS: List[str] = [
    "summary",
    "description",
    "issuetype",
    "priority",
    "status",
    "components",
    "labels",
    "fixVersions",
    "issuelinks",
    "attachment",
    "comment",
    "created",
    "updated",
]

# Bound every JQL search so a wide query can never return an unbounded page.
SEARCH_MAX_RESULTS = 25


class JiraError(Exception):
    """A Jira call failed. ``message`` is always safe to show to the user."""

    def __init__(self, message: str, http: Optional[int] = None, key: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.http = http
        self.key = key

    def to_dict(self) -> Dict[str, Any]:
        """Structured error shape from ``llm.md`` §6."""
        return {"error": True, "http": self.http, "message": self.message, "key": self.key}


def _base_url(config: Dict[str, str]) -> str:
    return (config.get("JIRA_BASE_URL") or "").strip().rstrip("/")


def _auth_kwargs(config: Dict[str, str]) -> Dict[str, Any]:
    email = (config.get("JIRA_EMAIL") or "").strip()
    token = (config.get("JIRA_TOKEN") or "").strip()
    if email:
        return {"auth": (email, token)}
    # Server / Data Center personal access token.
    return {"headers": {"Authorization": f"Bearer {token}"}}


def _require_config(config: Dict[str, str]) -> str:
    base = _base_url(config)
    if not base:
        raise JiraError("Jira Base URL is not configured. Set it on the Settings page.")
    if not (config.get("JIRA_TOKEN") or "").strip():
        raise JiraError("Jira API token is not configured. Set it on the Settings page.")
    return base


def _describe_http(status: int, key: Optional[str]) -> str:
    """Map a status code to an actionable, credential-free message."""
    target = f" {key}" if key else ""
    if status == 400:
        return f"Jira rejected the request{target} (HTTP 400). The query or field list is invalid."
    if status == 401:
        return (
            "Jira authentication failed (HTTP 401). The API token may be wrong or expired — "
            "generate a new one and update it on the Settings page."
        )
    if status == 403:
        return f"Jira denied access to{target} (HTTP 403). Your account lacks permission for this project."
    if status == 404:
        return f"Jira issue{target} was not found (HTTP 404). Check the key and your access."
    if status == 410:
        return (
            f"Jira reports this endpoint is gone (HTTP 410){target}. "
            "This instance has removed the legacy REST v2 API — the agent targets API v3."
        )
    if status == 429:
        return "Jira rate-limited the request (HTTP 429). Retries were exhausted."
    if status >= 500:
        return f"Jira is unavailable (HTTP {status}). Retries were exhausted."
    return f"Jira returned an unexpected error (HTTP {status}){target}."


def _request(
    method: str,
    url: str,
    config: Dict[str, str],
    key: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Issue a request with bounded retry on 429/5xx, then return the JSON body."""
    headers = {"Accept": "application/json"}
    headers.update(kwargs.pop("headers", {}))
    auth_kwargs = _auth_kwargs(config)
    headers.update(auth_kwargs.get("headers", {}))

    last_status: Optional[int] = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                auth=auth_kwargs.get("auth"),
                timeout=TIMEOUT_SECONDS,
                **kwargs,
            )
        except requests.exceptions.ConnectionError:
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_SECONDS * attempt)
                continue
            raise JiraError(
                f"Unable to reach Jira at {_base_url(config)}. Check the URL and your network."
            )
        except requests.exceptions.Timeout:
            if attempt < MAX_ATTEMPTS:
                time.sleep(BACKOFF_SECONDS * attempt)
                continue
            raise JiraError("Jira request timed out after several attempts.")
        except requests.exceptions.RequestException as exc:
            raise JiraError(f"Jira request failed: {exc.__class__.__name__}.")

        last_status = response.status_code
        if response.status_code in (429,) or response.status_code >= 500:
            if attempt < MAX_ATTEMPTS:
                retry_after = response.headers.get("Retry-After", "")
                delay = BACKOFF_SECONDS * attempt
                if retry_after.isdigit():
                    delay = min(float(retry_after), 10.0)
                time.sleep(delay)
                continue

        if response.status_code >= 400:
            raise JiraError(_describe_http(response.status_code, key), http=response.status_code, key=key)

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            raise JiraError("Jira returned an unreadable response body.")

    raise JiraError(_describe_http(last_status or 0, key), http=last_status, key=key)


def _fields_param(config: Dict[str, str]) -> str:
    fields = list(ISSUE_FIELDS)
    ac_field = (config.get("JIRA_AC_FIELD_ID") or "").strip()
    if ac_field and ac_field not in fields:
        fields.append(ac_field)
    return ",".join(fields)


def fetch_issue(issue_key: str, config: Dict[str, str]) -> Dict[str, Any]:
    """Fetch a single issue as raw JSON (REST v3)."""
    base = _require_config(config)
    url = f"{base}/rest/api/3/issue/{issue_key}?fields={_fields_param(config)}"
    return _request("GET", url, config, key=issue_key)


def fetch_comments(issue_key: str, config: Dict[str, str]) -> List[Dict[str, Any]]:
    """Fetch all comments for an issue (acceptance criteria often live here)."""
    base = _require_config(config)
    url = (
        f"{base}/rest/api/3/issue/{issue_key}/comment"
        f"?maxResults=100&orderBy=created"
    )
    data = _request("GET", url, config, key=issue_key)
    return data.get("comments", []) or []


def find_acceptance_criteria_field(config: Dict[str, str]) -> List[Dict[str, str]]:
    """Discover candidate acceptance-criteria custom fields on this instance."""
    base = _require_config(config)
    data = _request("GET", f"{base}/rest/api/3/field", config)
    matches: List[Dict[str, str]] = []
    for field in data if isinstance(data, list) else []:
        name = str(field.get("name", ""))
        if "acceptance" in name.lower() or "criteria" in name.lower():
            matches.append({"id": field.get("id", ""), "name": name})
    return matches


def search_issues(jql: str, config: Dict[str, str], max_results: int = SEARCH_MAX_RESULTS) -> List[Dict[str, Any]]:
    """Run a bounded JQL search via ``POST /rest/api/3/search/jql``.

    The legacy ``GET /search`` endpoint is deprecated on Cloud and returns 410
    on this instance, so the v3 POST form is the only path used here.
    """
    base = _require_config(config)
    url = f"{base}/rest/api/3/search/jql"
    body = {
        "jql": jql,
        "maxResults": max(1, min(max_results, SEARCH_MAX_RESULTS)),
        "fields": ["summary", "issuetype", "status", "priority", "created"],
    }
    data = _request("POST", url, config, json=body, headers={"Content-Type": "application/json"})
    return data.get("issues", []) or []


def list_projects(config: Dict[str, str]) -> List[Dict[str, str]]:
    """List the projects this account can see (used to validate a guessed key)."""
    base = _require_config(config)
    url = f"{base}/rest/api/3/project/search?maxResults=100"
    data = _request("GET", url, config)
    return [
        {"key": project.get("key", ""), "name": project.get("name", "")}
        for project in (data.get("values") or [])
        if project.get("key")
    ]


def latest_issue_key(project_key: str, config: Dict[str, str]) -> str:
    """Return the most recently created issue key in ``project_key``."""
    jql = f'project = "{project_key}" ORDER BY created DESC'
    issues = search_issues(jql, config, max_results=1)
    if not issues:
        raise JiraError(f"No tickets found in project {project_key} (or no access to it).")
    return issues[0].get("key", "")


def test_connection(config: Dict[str, str]) -> Dict[str, str]:
    """Verify credentials by fetching the authenticated user (``GET /myself``)."""
    base = _require_config(config)
    data = _request("GET", f"{base}/rest/api/3/myself", config)
    name = data.get("displayName") or data.get("name") or "authenticated user"
    return {"user": name, "message": f"Connected to Jira as {name}."}
