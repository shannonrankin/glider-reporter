"""Convert a GitHub function-submission issue into a Markdown function file."""

import argparse
import re
from pathlib import Path

import yaml

from functions.build_registry import build_registry


SUPPORTED_LANGUAGES = {"r", "python", "quarto"}
REQUIRED_SECTIONS = (
    "Function Name",
    "Short Description",
    "Language",
    "Execution Instructions",
    "Output Type",
    "Code / Snippet / Description",
)


def parse_sections(issue_body):
    """Return values grouped under level-three Markdown headings."""
    sections = {}
    heading = None
    for line in issue_body.splitlines():
        match = re.match(r"^###\s+(.+?)\s*$", line)
        if match:
            heading = match.group(1)
            sections[heading] = []
        elif heading is not None:
            sections[heading].append(line)

    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
    }


def function_id(name):
    """Convert a function name to a registry-safe identifier."""
    identifier = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not identifier:
        raise ValueError("Function Name must contain letters or numbers")
    return identifier


def checked_fields(value):
    """Extract checked values from a GitHub checkbox response."""
    return [
        match.group(1).strip()
        for line in value.splitlines()
        if (match := re.match(r"^\s*-\s*\[[xX]\]\s+(.+?)\s*$", line))
    ]


def function_metadata(issue_body, issue_url=""):
    """Convert a function-submission issue body to frontmatter metadata."""
    sections = parse_sections(issue_body)
    missing = [
        heading
        for heading in REQUIRED_SECTIONS
        if not sections.get(heading) or sections[heading] == "_No response_"
    ]
    if missing:
        raise ValueError(f"Missing required section(s): {', '.join(missing)}")

    name = sections["Function Name"]
    language = sections["Language"]
    identifier = function_id(name)
    language_key = language.casefold()
    return {
        "id": identifier,
        "name": name,
        "description": sections["Short Description"],
        "language": language,
        "execution_instructions": sections["Execution Instructions"],
        "translation_status": (
            "ready" if language_key in SUPPORTED_LANGUAGES else "needs_translation"
        ),
        "required_fields": checked_fields(
            sections.get("Required Data Fields", "")
        ),
        "output_type": sections["Output Type"],
        "citation": sections.get("Citation / Reference", "").replace(
            "_No response_", ""
        ),
        "issue_url": issue_url,
    }


def write_function_file(metadata, code, functions_dir):
    """Write one Markdown function file, rejecting duplicate identifiers."""
    functions_dir = Path(functions_dir)
    function_path = functions_dir / f"{metadata['id']}.md"
    if function_path.exists():
        raise ValueError(f"Function file already exists: {function_path}")

    functions_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(
        metadata, allow_unicode=True, sort_keys=False
    ).strip()
    function_path.write_text(
        f"---\n{frontmatter}\n---\n\n## Code\n\n{code.strip()}\n",
        encoding="utf-8",
    )
    return function_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a Markdown function file and rebuild registry.json."
    )
    parser.add_argument("issue_body", type=Path, help="Markdown issue body file")
    parser.add_argument(
        "--functions-dir",
        type=Path,
        default=Path("functions"),
        help="Directory for function Markdown files (default: functions)",
    )
    parser.add_argument("--issue-url", default="", help="Source GitHub issue URL")
    args = parser.parse_args()

    body = args.issue_body.read_text(encoding="utf-8")
    metadata = function_metadata(body, args.issue_url)
    write_function_file(
        metadata,
        parse_sections(body)["Code / Snippet / Description"],
        args.functions_dir,
    )
    build_registry(args.functions_dir, args.functions_dir / "registry.json")


if __name__ == "__main__":
    main()
