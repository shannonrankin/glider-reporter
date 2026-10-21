import json
import struct
import tempfile
import unittest
from pathlib import Path

from functions.build_registry import build_registry, frontmatter

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class FunctionRegistryTests(unittest.TestCase):
    def test_registry_is_compiled_from_function_frontmatter(self):
        registry_path = REPOSITORY_ROOT / "functions" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(
            item for item in registry if item["id"] == "temp_salinity_profile"
        )

        function_path = REPOSITORY_ROOT / entry["function_file"]
        self.assertTrue(function_path.is_file())
        self.assertEqual(frontmatter(function_path)["name"], entry["name"])
        self.assertIn("## Code", function_path.read_text(encoding="utf-8"))
        self.assertIn("execution_instructions", entry)

        with tempfile.TemporaryDirectory() as directory:
            rebuilt_path = Path(directory, "registry.json")
            rebuilt = build_registry(REPOSITORY_ROOT / "functions", rebuilt_path)
            self.assertEqual(rebuilt, registry)

        preview_path = (
            REPOSITORY_ROOT
            / "data"
            / "precomputed_outputs"
            / f"{entry['id']}.png"
        )
        with preview_path.open("rb") as preview:
            self.assertEqual(preview.read(8), b"\x89PNG\r\n\x1a\n")
            chunk_length, chunk_type = struct.unpack(">I4s", preview.read(8))
            self.assertEqual((chunk_length, chunk_type), (13, b"IHDR"))
            width, height = struct.unpack(">II", preview.read(8))
            preview.seek(-12, 2)
            self.assertEqual(
                preview.read(), b"\x00\x00\x00\x00IEND\xaeB`\x82"
            )

        self.assertGreater(width, 0)
        self.assertGreater(height, 0)

    def test_imported_plot_functions_have_python_and_r_entries(self):
        registry = json.loads(
            (
                REPOSITORY_ROOT / "functions" / "registry.json"
            ).read_text(encoding="utf-8")
        )
        entries = {entry["id"]: entry for entry in registry}

        for function_name in (
            "setup_map_axes",
            "plot_corr_matrix",
            "plot_spectrum_lines",
            "plot_box_by_group",
        ):
            for language, suffix in (("Python", "py"), ("R", "r")):
                entry = entries[f"{function_name}_{suffix}"]
                self.assertEqual(entry["language"], language)
                self.assertEqual(
                    entry["issue_url"],
                    "https://github.com/shannonrankin/glider-reporter/issues/38",
                )
                self.assertIn(
                    f"functions/{function_name}_{suffix}.md",
                    entry["function_file"],
                )


if __name__ == "__main__":
    unittest.main()
