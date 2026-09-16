from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ReportBuilderPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (REPOSITORY_ROOT / "report_builder.qmd").read_text(
            encoding="utf-8"
        )

    def test_page_loads_registry_mapping_and_bundle_dependencies(self):
        for expected in (
            'FileAttachment("functions/registry.json")',
            "glider_field_mapping.json",
            'require("jszip@3.10.1")',
            'require("file-saver@2.0.5")',
            "R/data_cleaner.R",
            "python/data_cleaner.py",
            "README.txt",
        ):
            self.assertIn(expected, self.page)

    def test_page_filters_compatible_functions_and_reports_missing_fields(self):
        for expected in (
            "report_builder_mapped_fields",
            "report_builder_available",
            "report_builder_incompatible",
            "requiredFields.every",
            "missing_fields",
            "Available Functions",
            "Incompatible Functions",
        ):
            self.assertIn(expected, self.page)

    def test_page_supports_selection_ordering_and_reactive_preview(self):
        for expected in (
            "viewof report_builder_selection",
            "report_builder_move",
            "Move up",
            "Move down",
            "viewof report_builder_format",
            "Quarto (.qmd)",
            "R Markdown (.Rmd)",
            "Python (.py)",
            "report_builder_document",
            "report_builder_preview",
        ):
            self.assertIn(expected, self.page)

    def test_page_packages_generated_report_sources_and_mapping(self):
        for expected in (
            "Download Report Bundle",
            "custom_glider_report.qmd",
            "custom_glider_report.Rmd",
            "custom_glider_report.py",
            'zip.folder("functions")',
            "entry.code_file",
            "report_builder_mapping_text",
        ):
            self.assertIn(expected, self.page)

    def test_page_uses_isolated_styles_and_is_linked_from_navigation(self):
        self.assertIn("styles/report_builder.scss", self.page)
        stylesheet = (
            REPOSITORY_ROOT / "styles" / "report_builder.scss"
        ).read_text(encoding="utf-8")
        self.assertIn(".report-builder {", stylesheet)
        self.assertNotIn(":root", stylesheet)

        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("href: report_builder.qmd", project)


if __name__ == "__main__":
    unittest.main()
