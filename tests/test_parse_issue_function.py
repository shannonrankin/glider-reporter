import json
import tempfile
import unittest
from pathlib import Path

from python.parse_issue_function import append_to_registry, registry_entry


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
        entry = registry_entry(ISSUE_BODY, "https://example.test/issues/1")

        self.assertEqual(entry["id"], "mixed_layer_depth")
        self.assertEqual(entry["translation_status"], "needs_translation")
        self.assertEqual(entry["required_fields"], ["depth", "temperature"])
        self.assertEqual(entry["code_file"], "")

    def test_quarto_is_ready_and_gets_code_path(self):
        entry = registry_entry(
            ISSUE_BODY.replace("Julia", "Quarto")
        )

        self.assertEqual(entry["translation_status"], "ready")
        self.assertEqual(
            entry["code_file"],
            "functions/quarto/mixed_layer_depth.qmd",
        )

    def test_entry_is_appended_to_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            registry_path = Path(directory, "registry.json")
            registry_path.write_text("[]\n", encoding="utf-8")

            append_to_registry(registry_entry(ISSUE_BODY), registry_path)

            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(len(registry), 1)
            self.assertEqual(registry[0]["name"], "Mixed Layer Depth")


if __name__ == "__main__":
    unittest.main()

