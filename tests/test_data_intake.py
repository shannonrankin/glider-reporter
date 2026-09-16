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
            "missingRequired",
            ".csv0",
        ):
            self.assertIn(expected, self.page)

    def test_page_uses_module_stylesheet(self):
        self.assertIn("styles/data_intake.scss", self.page)
        stylesheet = (
            REPOSITORY_ROOT / "styles" / "data_intake.scss"
        ).read_text(encoding="utf-8")
        self.assertIn(".data-intake {", stylesheet)

    def test_page_hides_ojs_and_provides_source_drawer(self):
        self.assertIn("execute:\n  echo: false", self.page)
        self.assertIn("Show Page Code / Logic", self.page)
        self.assertIn("data-intake__code-drawer", self.page)

    def test_source_cards_explain_each_option(self):
        for expected in (
            "Pre-loaded example oceanographic glider datasets",
            "Parse local oceanographic CSV files securely in your browser",
            "Stream public dataset records directly from IOOS GliderDAC",
        ):
            self.assertIn(expected, self.page)

    def test_page_shows_loaded_dataset_details(self):
        for expected in (
            "Loaded Datasets & Status",
            "rows loaded",
            "Detected columns",
            "normalized to snake_case",
            "Proceed to Step 2",
        ):
            self.assertIn(expected, self.page)

    def test_acknowledgment_uses_prominent_button(self):
        self.assertNotIn("Inputs.toggle", self.page)
        self.assertIn(
            'data-intake__button data-intake__button--proceed',
            self.page,
        )
        self.assertIn("Acknowledged & Unlocked", self.page)

    def test_quarto_project_has_static_output_directory(self):
        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("type: website", project)
        self.assertIn("output-dir: _site", project)


if __name__ == "__main__":
    unittest.main()
