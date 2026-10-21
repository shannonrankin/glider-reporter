"""Compile function Markdown frontmatter into the browser registry."""

import argparse
import json
from pathlib import Path

import yaml


REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "language",
    "execution_instructions",
    "required_fields",
    "output_type",
    "translation_status",
    "citation",
    "issue_url",
}


def frontmatter(function_path):
    """Read YAML frontmatter from one function Markdown file."""
    content = function_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{function_path} is missing YAML frontmatter")

    _, separator, remainder = content.partition("\n---\n")
    if not separator:
        raise ValueError(f"{function_path} has unclosed YAML frontmatter")

    metadata = yaml.safe_load(content[4 : content.index("\n---\n")])
    if not isinstance(metadata, dict):
        raise ValueError(f"{function_path} frontmatter must be a mapping")
    return metadata


def build_registry(functions_dir, registry_path):
    """Write a sorted JSON registry compiled from Markdown frontmatter."""
    functions_dir = Path(functions_dir)
    registry_path = Path(registry_path)
    entries = []
    identifiers = set()

    for function_path in sorted(functions_dir.glob("*.md")):
        metadata = frontmatter(function_path)
        missing = REQUIRED_FIELDS - metadata.keys()
        if missing:
            raise ValueError(
                f"{function_path} is missing required field(s): "
                f"{', '.join(sorted(missing))}"
            )
        if not isinstance(metadata["required_fields"], list):
            raise ValueError(f"{function_path} required_fields must be a list")
        if metadata["id"] in identifiers:
            raise ValueError(f"Duplicate function id: {metadata['id']}")

        identifiers.add(metadata["id"])
        entries.append(
            {
                **metadata,
                "function_file": function_path.relative_to(
                    functions_dir.parent
                ).as_posix(),
            }
        )

    registry_path.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Compile functions/*.md frontmatter into registry.json."
    )
    parser.add_argument(
        "--functions-dir",
        type=Path,
        default=Path("functions"),
        help="Directory containing function Markdown files",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("functions/registry.json"),
        help="Compiled registry path",
    )
    args = parser.parse_args()
    build_registry(args.functions_dir, args.registry)


if __name__ == "__main__":
    main()
