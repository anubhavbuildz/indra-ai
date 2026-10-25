"""Load editable agent system prompts from packaged role Markdown files."""

from pathlib import Path
from typing import Literal

RoleFile = Literal["terraform_role.md", "compliance_role.md", "senior_role.md"]
ROLE_DIRECTORY = Path(__file__).with_name("roles")


def _normalize_prompt(content: str) -> str:
    return "\n\n".join(" ".join(paragraph.split()) for paragraph in content.split("\n\n"))


def load_role_prompt(role_file: RoleFile, section: str | None = None) -> str:
    """Read a role prompt from disk, optionally selecting a level-two section."""
    content = _normalize_prompt((ROLE_DIRECTORY / role_file).read_text(encoding="utf-8").strip())
    if section is None:
        return content

    lines = content.splitlines()
    heading = f"## {section}"
    try:
        start = lines.index(heading) + 1
    except ValueError as exc:
        raise ValueError(f"Prompt section {section!r} is missing from {role_file}.") from exc

    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    prompt = _normalize_prompt("\n".join(lines[start:end]).strip())
    if not prompt:
        raise ValueError(f"Prompt section {section!r} is empty in {role_file}.")
    return prompt
