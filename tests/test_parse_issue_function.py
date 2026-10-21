import tempfile
import unittest
from pathlib import Path

from functions.build_registry import build_registry, frontmatter
from python.parse_issue_function import function_metadata, write_function_file


ISSUE_BODY = """\
### Function Name

Mixed Layer Depth

### Short Description

Calculates mixed layer depth.

### Language

Julia

### Execution Instructions

Run with Julia 1.x.

### Required Data Fields

- [x] depth
- [x] temperature
- [ ] salinity

### Output Type

Summary Text

### Code / Snippet / Description

Example implementation.

### Citation / Reference

Example method
"""


class ParseIssueFunctionTests(unittest.TestCase):
    def test_non_target_language_needs_translation(self):
        entry = function_metadata(ISSUE_BODY, "https://example.test/issues/1")

        self.assertEqual(entry["id"], "mixed_layer_depth")
        self.assertEqual(entry["translation_status"], "needs_translation")
        self.assertEqual(entry["required_fields"], ["depth", "temperature"])
        self.assertEqual(entry["execution_instructions"], "Run with Julia 1.x.")

    def test_quarto_is_ready(self):
        entry = function_metadata(
            ISSUE_BODY.replace("Julia", "Quarto")
        )

        self.assertEqual(entry["translation_status"], "ready")

    def test_function_file_is_written_and_compiled_into_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            functions_dir = Path(directory, "functions")
            metadata = function_metadata(ISSUE_BODY)
            function_path = write_function_file(
                metadata,
                "```julia\nExample implementation.\n```",
                functions_dir,
            )

            self.assertEqual(frontmatter(function_path), metadata)
            self.assertIn("## Code", function_path.read_text(encoding="utf-8"))

            registry_path = functions_dir / "registry.json"
            registry = build_registry(functions_dir, registry_path)
            self.assertEqual(len(registry), 1)
            self.assertEqual(registry[0]["name"], "Mixed Layer Depth")
            self.assertEqual(
                registry[0]["function_file"],
                "functions/mixed_layer_depth.md",
            )


if __name__ == "__main__":
    unittest.main()
