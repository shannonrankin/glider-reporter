import json
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class WebsiteDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        cls.home = (REPOSITORY_ROOT / "index.qmd").read_text(encoding="utf-8")
        cls.references = (REPOSITORY_ROOT / "references.qmd").read_text(
            encoding="utf-8"
        )

    def test_navbar_links_all_pages_and_github_repository(self):
        expected_links = (
            "href: index.qmd",
            "href: data_intake.qmd",
            "href: function_explorer.qmd",
            "href: report_builder.qmd",
            "href: references.qmd",
        )
        positions = [self.project.index(link) for link in expected_links]

        self.assertEqual(positions, sorted(positions))
        self.assertIn("icon: github", self.project)
        self.assertIn(
            "https://github.com/shannonrankin/glider-reporter", self.project
        )

    def test_workflow_deploys_rendered_site_to_github_pages(self):
        workflow = (
            REPOSITORY_ROOT / ".github" / "workflows" / "publish_quarto.yml"
        ).read_text(encoding="utf-8")

        for expected in (
            "quarto render",
            "uses: actions/upload-pages-artifact@v4",
            "path: _site",
            "uses: actions/deploy-pages@v4",
            "pages: write",
            "id-token: write",
        ):
            self.assertIn(expected, workflow)

    def test_home_documents_primary_user_workflows(self):
        for expected in (
            "## Build a report in three steps",
            "### 1. Upload data and map fields",
            "### 2. Choose reporting functions",
            "### 3. Build and download the report",
            "## Contribute a reporting function",
            "issues/new?template=function_submission.yml",
            "## Translate an existing function",
            "## Use this repository as a template",
            "git clone https://github.com/shannonrankin/glider-reporter.git",
        ):
            self.assertIn(expected, self.home)

    def test_references_loads_registry_and_discloses_ai_use(self):
        for expected in (
            'FileAttachment("functions/registry.json")',
            "entry.citation",
            "entry.name",
            "entry.code_file",
            "entry.issue_url",
            "## AI governance disclosure",
            "GitHub Copilot",
            "large-language-model assistants",
        ):
            self.assertIn(expected, self.references)

    def test_registry_entries_supply_bibliography_metadata(self):
        registry = json.loads(
            (REPOSITORY_ROOT / "functions" / "registry.json").read_text(
                encoding="utf-8"
            )
        )
        required_fields = {"id", "name", "language", "citation", "issue_url", "code_file"}

        self.assertGreater(len(registry), 0)
        for entry in registry:
            self.assertTrue(required_fields.issubset(entry))
            self.assertTrue(entry["citation"])
            self.assertTrue(entry["issue_url"])


if __name__ == "__main__":
    unittest.main()
