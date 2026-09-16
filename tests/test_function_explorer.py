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
            "entry.code_file",
        ):
            self.assertIn(expected, self.page)

    def test_page_has_reactive_search_and_filters(self):
        for expected in (
            "viewof function_explorer_search",
            "viewof function_explorer_required_fields",
            "viewof function_explorer_language",
            "viewof function_explorer_output_type",
            "function_explorer_chip_input",
            "function-explorer__filter-card",
            '"aria-pressed"',
            "function_explorer_matches",
            "selectedFields.every",
        ):
            self.assertIn(expected, self.page)

        self.assertNotIn("Inputs.select(", self.page)

    def test_page_has_cards_and_accessible_detail_drawer(self):
        for expected in (
            "function-explorer__card",
            "function-explorer__drawer",
            "function-explorer__drawer-header",
            "function-explorer__drawer-body",
            "function-explorer__drawer-footer",
            "function-explorer__drawer-expand",
            "function-explorer__drawer--full-screen",
            '"role", "dialog"',
            '"aria-modal", "true"',
            "View details",
            "Close (✕)",
            "Expand Full Screen",
            "Normal View",
            "Needs translation",
            "View Build History on GitHub",
        ):
            self.assertIn(expected, self.page)

        self.assertNotIn("function-explorer__card-link", self.page)

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
        self.assertIn(".function-explorer__drawer-body", stylesheet)
        self.assertIn("overflow-y: auto", stylesheet)
        self.assertIn("width: 500px", stylesheet)
        self.assertIn("width: 100vw", stylesheet)
        self.assertIn("background: rgba(0, 0, 0, 0.45)", stylesheet)
        self.assertIn("z-index: 1000", stylesheet)
        self.assertIn("z-index: 1001", stylesheet)
        self.assertNotIn(":root", stylesheet)

    def test_site_navigation_links_to_explorer(self):
        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("href: function_explorer.qmd", project)


if __name__ == "__main__":
    unittest.main()
