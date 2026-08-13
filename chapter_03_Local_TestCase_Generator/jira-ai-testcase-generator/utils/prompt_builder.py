"""Build the prompt sent to the AI model.

The prompt is deliberately concise so a small local model (Gemma 3 1B) can
follow it reliably: role, grounded requirements, the template, and a short
constraint list. Nothing here depends on which provider will serve the prompt.
"""

from __future__ import annotations

from .jira_parser import parse_issue
from .template_loader import load_template


def build_test_case_prompt(
    issue: dict,
    config: dict,
    template_content: str | None = None,
) -> str:
    """Assemble the final test case generation prompt.

    Args:
        issue: Parsed Jira issue dict (see ``parse_issue``).
        config: Application configuration (used for template path).
        template_content: Optional pre-loaded template text; loads from disk
            when omitted.

    Returns:
        The complete prompt string.
    """
    requirements = issue.get("requirement_context", "")
    template = template_content or load_template(config.get("TEMPLATE_PATH"))

    return f"""ROLE:
You are a Senior QA Engineer.

TASK:
Generate comprehensive test cases based ONLY on the Jira requirements below.
Do not invent features or behavior that is not documented.

JIRA REQUIREMENTS:
{requirements}

TEST CASE TEMPLATE:
{template}

CONSTRAINTS:
- Use only the provided Jira requirements.
- Do not invent undocumented functionality.
- Cover positive and negative scenarios.
- Include boundary cases only where supported by the requirements.
- If information is missing, write "Not specified".
- Follow the supplied template exactly.
- Output the test cases as a Markdown table (or the template format shown above).
"""
