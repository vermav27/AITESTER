"""Page 1 — Chat / Test Case Generator.

Entry point of the Streamlit app. The user enters a natural-language request
such as "Create test cases for ABC-123", the app extracts the Jira ID, fetches
the ticket, loads the template, builds a prompt, and generates test cases via
the configured AI provider.
"""

from __future__ import annotations

import re

import streamlit as st

from services import jira_service, llm_service
from utils import config_manager, jira_parser, prompt_builder, template_loader

st.set_page_config(page_title="Jira AI Test Case Generator", page_icon="🧪", layout="centered")

JIRA_ID_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d{1,6})\b")


def extract_jira_id(prompt: str) -> str | None:
    """Return the first Jira issue key found in ``prompt`` or None."""
    match = JIRA_ID_PATTERN.search(prompt)
    return match.group(1) if match else None


def run_generation(prompt: str) -> None:
    """Execute the full pipeline: extract ID → fetch → template → prompt → LLM."""
    jira_id = extract_jira_id(prompt)
    if not jira_id:
        st.error(
            "Could not identify a Jira ticket ID in your request. "
            'Try something like "Create test cases for ABC-123".'
        )
        return

    config = config_manager.load_config()

    with st.spinner(f"Fetching Jira requirements for {jira_id}..."):
        try:
            raw_issue = jira_service.fetch_issue(jira_id, config)
        except jira_service.JiraServiceError as exc:
            st.error(str(exc))
            return
        issue = jira_parser.parse_issue(raw_issue, config)

    with st.spinner("Loading test case template..."):
        try:
            template = template_loader.load_template()
        except template_loader.TemplateNotFoundError as exc:
            st.error(str(exc))
            return

    prompt_text = prompt_builder.build_test_case_prompt(issue, config, template)

    with st.spinner("Generating test cases..."):
        try:
            content, provider_used = llm_service.generate_response(prompt_text, config)
        except llm_service.LLMServiceError as exc:
            st.error(str(exc))
            return

    st.success(f"Generated with **{provider_used}** for **{jira_id}**.")
    st.markdown(content)


st.title("🧪 Jira AI Test Case Generator")
st.caption("Ask for test cases based on a Jira ticket — powered by your local Ollama model.")

# Store the last prompt in session state so it survives a rerun.
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

with st.form("chat_form", clear_on_submit=True):
    user_prompt = st.text_input(
        "Your request",
        placeholder='e.g. Create test cases for PROJ-123',
    )
    submitted = st.form_submit_button("Send", type="primary")

if submitted:
    if not user_prompt.strip():
        st.warning("Please enter a request first.")
    else:
        st.session_state.last_prompt = user_prompt
        st.session_state.last_result = None
        st.rerun()

if st.session_state.last_prompt and st.session_state.last_result is None:
    st.session_state.last_result = "pending"
    with st.container(border=True):
        st.markdown(f"**You:** {st.session_state.last_prompt}")
        run_generation(st.session_state.last_prompt)
    st.session_state.last_result = "done"

# Show the last conversation if a generation already ran.
if st.session_state.last_result == "done" and st.session_state.last_prompt:
    st.markdown("---")
    st.caption("Previous session output is displayed above. Enter a new request to generate again.")
