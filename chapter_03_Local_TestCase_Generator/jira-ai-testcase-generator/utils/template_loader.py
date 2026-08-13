"""Load the test case template from the ``templates/`` folder.

The template file is the source of truth for the generated output format. It
is read from disk on every request so edits to the file take effect without a
restart, and it is never hardcoded into the application code.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = PROJECT_ROOT / "templates" / "test_case_template.md"


class TemplateNotFoundError(Exception):
    """Raised when the template file cannot be located or read."""


def load_template(template_path: Path | str | None = None) -> str:
    """Return the contents of the test case template.

    Args:
        template_path: Optional override path; defaults to
            ``templates/test_case_template.md``.

    Raises:
        TemplateNotFoundError: If the file does not exist.
    """
    path = Path(template_path) if template_path else DEFAULT_TEMPLATE
    if not path.is_file():
        raise TemplateNotFoundError(
            f"Test case template not found at {path}. "
            "Create templates/test_case_template.md (see .env.example)."
        )
    return path.read_text(encoding="utf-8")
