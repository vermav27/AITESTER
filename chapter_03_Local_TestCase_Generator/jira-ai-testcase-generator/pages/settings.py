"""Page 2 — Settings / Configuration.

Edit Jira, Ollama, and Groq settings, save them to ``.env``, and test each
connection. Secret values are masked in the UI and never displayed in plain
text; only newly typed values are saved.
"""

from __future__ import annotations

import streamlit as st

from services import groq_service, jira_service, ollama_service
from utils import config_manager

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")

st.title("⚙️ Settings")
st.caption("Save your configuration once; it is stored locally in a gitignored .env file.")


def render_connection_test(label: str, fn) -> None:
    """Run a connection test and show a ✓/✗ result with a safe message."""
    try:
        fn()
        st.success(f"✓ {label} connection successful")
    except Exception as exc:  # noqa: BLE001 — any service error is user-safe
        st.error(f"✗ Unable to connect to {label}: {exc}")


def main() -> None:
    config = config_manager.load_config()

    st.subheader("AI Provider")
    provider = st.radio(
        "Primary AI provider",
        options=["ollama", "groq"],
        index=0 if config.get("AI_PROVIDER", "ollama").lower() != "groq" else 1,
        horizontal=True,
        help="Ollama is local and free. Groq is used if Ollama is unreachable and a key is set.",
    )

    st.subheader("Jira Configuration")
    jira_base = st.text_input("Jira Base URL", value=config.get("JIRA_BASE_URL", ""),
                              placeholder="https://your-domain.atlassian.net")
    jira_email = st.text_input("Jira Email ID", value=config.get("JIRA_EMAIL", ""),
                               placeholder="you@example.com")
    jira_token = st.text_input(
        "Jira API Token",
        value="",
        placeholder=config_manager.mask_secret(config.get("JIRA_API_TOKEN", "")) or "Enter your API token",
        type="password",
        help="Token is masked. Leave blank to keep the saved value.",
    )

    st.subheader("Ollama Configuration")
    ollama_base = st.text_input("Ollama Base URL", value=config.get("OLLAMA_BASE_URL", ""),
                                placeholder="http://localhost:11434")
    ollama_model = st.text_input("Ollama Model Name", value=config.get("OLLAMA_MODEL", ""),
                                 placeholder="gemma3:4b")

    st.subheader("Groq Configuration")
    groq_key = st.text_input(
        "Groq API Key",
        value="",
        placeholder=config_manager.mask_secret(config.get("GROQ_API_KEY", "")) or "Enter your Groq API key",
        type="password",
        help="Key is masked. Leave blank to keep the saved value.",
    )
    groq_model = st.text_input("Groq Model", value=config.get("GROQ_MODEL", ""),
                               placeholder="llama-3.3-70b-versatile")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Configuration", type="primary", use_container_width=True):
            config_manager.save_config(
                {
                    "JIRA_BASE_URL": jira_base,
                    "JIRA_EMAIL": jira_email,
                    "JIRA_API_TOKEN": jira_token,
                    "OLLAMA_BASE_URL": ollama_base,
                    "OLLAMA_MODEL": ollama_model,
                    "GROQ_API_KEY": groq_key,
                    "GROQ_MODEL": groq_model,
                    "AI_PROVIDER": provider,
                }
            )
            st.success("Configuration saved.")
    with col2:
        st.caption("")

    st.subheader("Connection Tests")
    test_cols = st.columns(3)
    cfg = config_manager.load_config()  # fresh after any save
    with test_cols[0]:
        if st.button("Test Jira Connection", use_container_width=True):
            render_connection_test("Jira", lambda: jira_service.test_connection(cfg))
    with test_cols[1]:
        if st.button("Test Ollama Connection", use_container_width=True):
            render_connection_test("Ollama", lambda: ollama_service.test_connection(cfg))
    with test_cols[2]:
        if st.button("Test Groq Connection", use_container_width=True):
            render_connection_test("Groq", lambda: groq_service.test_connection(cfg))


main()
