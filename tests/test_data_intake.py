from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class DataIntakePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (REPOSITORY_ROOT / "data_intake.qmd").read_text(encoding="utf-8")

    def test_page_references_all_supported_sources(self):
        for expected in (
            "data/sample/og10_standard/glider_og10_data.csv",
            "data/sample/custom_hackathon/glider_hackathon_data.csv",
            "data/sample/custom_hackathon/glider_hackathon_fieldDefinitions.csv",
            "Upload Custom CSV",
            "GliderDAC / ERDDAP",
        ):
            self.assertIn(expected, self.page)

    def test_page_includes_mapping_persistence_and_required_validation(self):
        for expected in (
            "glider_field_mapping.json",
            "Import Field Mapping",
            "Download Field Mapping",
            '"latitude", "longitude", "time"',
            "Acknowledge & Proceed to Dashboard",
        ):
            self.assertIn(expected, self.page)

    def test_page_uses_module_stylesheet(self):
        self.assertIn("styles/data_intake.scss", self.page)
        stylesheet = (
            REPOSITORY_ROOT / "styles" / "data_intake.scss"
        ).read_text(encoding="utf-8")
        self.assertIn(".data-intake {", stylesheet)

    def test_quarto_project_has_static_output_directory(self):
        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("type: website", project)
        self.assertIn("output-dir: _site", project)


if __name__ == "__main__":
    unittest.main()
