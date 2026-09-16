import json
import struct
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class FunctionRegistryTests(unittest.TestCase):
    def test_sample_entry_assets_are_available(self):
        registry_path = REPOSITORY_ROOT / "functions" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(
            item for item in registry if item["id"] == "temp_salinity_profile"
        )

        self.assertTrue((REPOSITORY_ROOT / entry["code_file"]).is_file())

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


if __name__ == "__main__":
    unittest.main()
