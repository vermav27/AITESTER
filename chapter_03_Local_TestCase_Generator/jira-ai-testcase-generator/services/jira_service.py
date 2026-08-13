"""Jira REST API client.

Handles only Jira communication: fetching issues by key and testing the
connection. Credentials come from the config dict — never hardcoded — and
error messages never include the token or authorization header.
"""

from __future__ import annotations

from typing import Dict, Any

import requests

TIMEOUT_SECONDS = 20


class JiraServiceError(Exception):
    """Raised when a Jira request fails. Message is always user-safe."""


def _auth(config: Dict[str, str]) -> tuple[str, str]:
    """Return the (email, API token) tuple used by requests' Basic auth."""
    email = config.get("JIRA_EMAIL", "").strip()
    token = config.get("JIRA_API_TOKEN", "").strip()
    return (email, token)


def _base_url(config: Dict[str, str]) -> str:
    return config.get("JIRA_BASE_URL", "").strip().rstrip("/")


def fetch_issue(issue_key: str, config: Dict[str, str]) -> Dict[str, Any]:
    """Fetch a Jira issue by key and return its raw JSON payload."""
    base = _base_url(config)
    if not base:
        raise JiraServiceError("Jira Base URL is not configured.")
    if not config.get("JIRA_EMAIL") or not config.get("JIRA_API_TOKEN"):
        raise JiraServiceError("Jira Email or API Token is not configured.")

    url = f"{base}/rest/api/3/issue/{issue_key}"
    try:
        response = requests.get(url, auth=_auth(config), timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise JiraServiceError(f"Unable to reach Jira at {base}. Check the URL and network.")
    except requests.exceptions.Timeout:
        raise JiraServiceError("Jira request timed out. Check your network and try again.")
    except requests.exceptions.RequestException as exc:
        raise JiraServiceError(f"Jira request failed: {exc.__class__.__name__}")

    if response.status_code == 404:
        raise JiraServiceError(f"Jira issue {issue_key} was not found.")
    if response.status_code == 401 or response.status_code == 403:
        raise JiraServiceError("Jira authentication failed. Check your email and API token.")
    if response.status_code >= 400:
        raise JiraServiceError(f"Jira returned an error (HTTP {response.status_code}).")

    return response.json()


def test_connection(config: Dict[str, str]) -> None:
    """Verify the Jira connection by fetching the current user.

    Raises JiraServiceError with a user-safe message on failure.
    """
    base = _base_url(config)
    if not base:
        raise JiraServiceError("Jira Base URL is not configured.")
    if not config.get("JIRA_EMAIL") or not config.get("JIRA_API_TOKEN"):
        raise JiraServiceError("Jira Email or API Token is not configured.")

    url = f"{base}/rest/api/3/myself"
    try:
        response = requests.get(url, auth=_auth(config), timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise JiraServiceError(f"Unable to reach Jira at {base}. Check the URL and network.")
    except requests.exceptions.Timeout:
        raise JiraServiceError("Jira request timed out. Check your network and try again.")
    except requests.exceptions.RequestException as exc:
        raise JiraServiceError(f"Jira request failed: {exc.__class__.__name__}")

    if response.status_code == 401 or response.status_code == 403:
        raise JiraServiceError("Jira authentication failed. Check your email and API token.")
    if response.status_code >= 400:
        raise JiraServiceError(f"Jira returned an error (HTTP {response.status_code}).")
