from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class FunctionExplorerPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (REPOSITORY_ROOT / "function_explorer.qmd").read_text(
            encoding="utf-8"
        )

    def test_page_loads_registry_and_preview_assets(self):
        for expected in (
            'FileAttachment("functions/registry.json")',
            "data/precomputed_outputs/",
            "entry.issue_url",
            "entry.citation",
            "entry.execution_instructions",
            "entry.function_file",
            "Download Function Source",
        ):
            self.assertIn(expected, self.page)

    def test_page_has_reactive_search_and_filters(self):
        for expected in (
            "viewof function_explorer_search",
            "viewof function_explorer_required_fields",
            "viewof function_explorer_language",
            "viewof function_explorer_output_type",
            'FileAttachment("data/standard_fields.csv").csv()',
            "entry.standard_field",
            "function_explorer_chip_input",
            "function-explorer__filter-card",
            '"aria-pressed"',
            "function_explorer_matches",
            "selectedFields.every",
        ):
            self.assertIn(expected, self.page)

        self.assertNotIn("function_explorer_standard_fields = [", self.page)

    def test_page_has_inline_detail_navigation_and_selection_handoff(self):
        for expected in (
            "Inputs.select(options",
            "viewof function_explorer_active_id",
            "Previous (←)",
            "Next (→)",
            "% function_explorer_matches.length",
            "function-explorer__detail-card",
            "function-explorer__code",
            "Needs translation",
            "View Build History on GitHub",
            "Select for Report",
            "function_explorer_selected",
            'localStorage.setItem("glider_reporter_selected_functions"',
            'window.location.assign("report_builder.qmd")',
        ):
            self.assertIn(expected, self.page)

        self.assertNotIn("function-explorer__drawer", self.page)
        self.assertNotIn("function-explorer__overlay", self.page)

    def test_page_uses_isolated_module_styles(self):
        self.assertIn("styles/function_explorer.scss", self.page)
        stylesheet = (
            REPOSITORY_ROOT / "styles" / "function_explorer.scss"
        ).read_text(encoding="utf-8")
        self.assertIn(".function-explorer {", stylesheet)
        self.assertIn("grid-column: 1 / -1", stylesheet)
        self.assertIn(".function-explorer__chip--active", stylesheet)
        self.assertIn(".function-explorer__filter-card", stylesheet)
        self.assertIn(".function-explorer__search form > label", stylesheet)
        self.assertIn(".function-explorer__navigation", stylesheet)
        self.assertIn(".function-explorer__detail-card", stylesheet)
        self.assertIn(".function-explorer__report-action", stylesheet)
        self.assertIn(".function-explorer__code", stylesheet)
        self.assertNotIn(":root", stylesheet)

    def test_site_navigation_links_to_explorer(self):
        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("href: function_explorer.qmd", project)


if __name__ == "__main__":
    unittest.main()
