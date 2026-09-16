"""Append a GitHub function-submission issue to the function registry."""

import argparse
import json
import re
from pathlib import Path


SUPPORTED_LANGUAGES = {"r", "python", "quarto"}
CODE_FILE_SUFFIXES = {"r": ".Rmd", "python": ".py", "quarto": ".qmd"}
REQUIRED_SECTIONS = (
    "Function Name",
    "Short Description",
    "Language",
    "Output Type",
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


def registry_entry(issue_body, issue_url=""):
    """Convert a function-submission issue body to registry metadata."""
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
    suffix = CODE_FILE_SUFFIXES.get(language_key)
    code_file = (
        f"functions/{language_key}/{identifier}{suffix}" if suffix else ""
    )

    return {
        "id": identifier,
        "name": name,
        "description": sections["Short Description"],
        "language": language,
        "translation_status": (
            "ready" if language_key in SUPPORTED_LANGUAGES else "needs_translation"
        ),
        "required_fields": checked_fields(
            sections.get("Required Data Fields", "")
        ),
        "output_type": sections["Output Type"],
        "code_file": code_file,
        "citation": sections.get("Citation / Reference", "").replace(
            "_No response_", ""
        ),
        "issue_url": issue_url,
    }


def append_to_registry(entry, registry_path):
    """Append an entry to a JSON registry, rejecting duplicate identifiers."""
    registry_path = Path(registry_path)
    with registry_path.open(encoding="utf-8") as registry_file:
        registry = json.load(registry_file)

    if not isinstance(registry, list):
        raise ValueError("Registry must contain a JSON array")
    if any(item.get("id") == entry["id"] for item in registry):
        raise ValueError(f"Registry already contains id: {entry['id']}")

    registry.append(entry)
    with registry_path.open("w", encoding="utf-8") as registry_file:
        json.dump(registry, registry_file, indent=2, ensure_ascii=False)
        registry_file.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Append a function-submission issue body to registry.json."
    )
    parser.add_argument("issue_body", type=Path, help="Markdown issue body file")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("functions/registry.json"),
        help="Registry JSON path (default: functions/registry.json)",
    )
    parser.add_argument("--issue-url", default="", help="Source GitHub issue URL")
    args = parser.parse_args()

    body = args.issue_body.read_text(encoding="utf-8")
    append_to_registry(registry_entry(body, args.issue_url), args.registry)


if __name__ == "__main__":
    main()

