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
            "Load Sample Dataset",
            "Upload Custom Dataset",
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
            "Built-in example oceanographic glider datasets",
            "Parse local oceanographic CSV, RData, HDF5, and NetCDF files",
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

    def test_upload_accepts_and_dispatches_all_supported_formats(self):
        for expected in (
            ".csv,text/csv",
            ".rdata,.rda",
            ".h5,.hdf5,application/x-hdf",
            ".nc,.netcdf,application/x-netcdf",
            "data_intake_parse_csv",
            "data_intake_parse_netcdf",
            "data_intake_parse_hdf5",
            "data_intake_parse_rdata",
            "data_intake_parse_upload",
            "await upload.arrayBuffer()",
        ):
            self.assertIn(expected, self.page)

    def test_binary_parsers_flatten_and_normalize_detected_variables(self):
        for expected in (
            "data_intake_flatten_variables",
            "data_intake_unique_headers(included.map",
            "shape.length > 2",
            "No tabular 1D or 2D variables could be extracted",
            "dimensions do not align",
            "reader.recordDimension.length",
            'variable.type === "char"',
            "column.endsWith(`_${alias}`)",
        ):
            self.assertIn(expected, self.page)

    def test_recursive_flattening_uses_a_local_function_name(self):
        self.assertIn(
            "data_intake_flatten_values = function flattenValues(value)",
            self.page,
        )
        self.assertIn("return value.flatMap(flattenValues);", self.page)
        self.assertNotIn(
            "value.flatMap((item) => data_intake_flatten_values(item))",
            self.page,
        )

    def test_dataset_status_shows_format_metadata_and_guidance(self):
        for expected in (
            "CSV Text",
            "NetCDF (OG1.0)",
            "HDF5 Container",
            "RData Frame",
            "columns extracted",
            "data-intake__format-badge",
            "Extraction guidance",
            "data-intake__extraction-guidance",
        ):
            self.assertIn(expected, self.page)

    def test_acknowledgment_uses_prominent_button(self):
        self.assertNotIn("Inputs.toggle", self.page)
        self.assertIn(
            'data-intake__button data-intake__button--proceed',
            self.page,
        )
        self.assertIn("Acknowledged & Unlocked", self.page)

    def test_page_has_empty_initial_state_and_reset_control(self):
        for expected in (
            'name: "No dataset selected"',
            "data_intake_source_control.value = null",
            "data_intake_upload_control",
            "data_intake_erddap_control.value =",
            "data_intake_mapping_file_control",
            "Clear Dataset",
        ):
            self.assertIn(expected, self.page)
        self.assertNotIn('{label: "Data source", value: "sample"}', self.page)

    def test_page_warns_for_unmapped_optional_fields(self):
        for expected in (
            "data_intake_optional_fields",
            "data_intake_optional_warnings",
            "Optional OG1.0 Fields Not Mapped",
            "data-intake__optional-warning",
        ):
            self.assertIn(expected, self.page)

    def test_dashboard_unlock_has_strict_guardrails(self):
        for expected in (
            "data_intake_loaded.error === null",
            "data_intake_loaded.rows.length > 0",
            "data_intake_validation.missingRequired.length === 0",
            "const validationAccepted = data_intake_validation.issues.length === 0",
            "Dashboard Generation Unlocked",
            "Dashboard Generation Locked",
            "Load a dataset with at least one valid row.",
            "Resolve the data source error:",
            "Map required fields:",
            "Review and acknowledge the coordinate or timestamp red flags.",
        ):
            self.assertIn(expected, self.page)

    def test_copilot_instructions_include_data_intake_standards(self):
        instructions = (
            REPOSITORY_ROOT / ".github" / "copilot-instructions.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "Interactive Data Intake State & Validation Standards",
            "Explicit Data Source Selection",
            "Clear & Reset Capabilities",
            "Field Mapping Warnings",
            "Strict Unlock Safeguards",
        ):
            self.assertIn(expected, instructions)

    def test_copilot_instructions_include_multiformat_guidelines(self):
        instructions = (
            REPOSITORY_ROOT / ".github" / "copilot-instructions.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "Multi-Format Binary Data Intake Guidelines",
            ".csv`, `.rdata`, `.rda`, `.h5`, `.hdf5`, `.nc`, and `.netcdf",
            "Parse NetCDF",
            "Parse HDF5",
            "Parse RData",
            "strict `snake_case`",
        ):
            self.assertIn(expected, instructions)

    def test_quarto_project_has_static_output_directory(self):
        project = (REPOSITORY_ROOT / "_quarto.yml").read_text(encoding="utf-8")
        self.assertIn("type: website", project)
        self.assertIn("output-dir: _site", project)


if __name__ == "__main__":
    unittest.main()
