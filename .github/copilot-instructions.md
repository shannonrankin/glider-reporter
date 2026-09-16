# Repository Instructions & Conventions

## Architecture & Framework
- Framework: Quarto published to GitHub Pages (no external backend servers).
- Interactivity: Free & open-source client-side tools only (Observable JS/ojs, WebAssembly).
- Domain: Scientific research (NOAA Fisheries / marine science focus).
- Nature: Template repository; code must be accessible to novice R users.
- Directory Structure: Data (`data/`), Outputs (`output/`), Supplementary (`supplement/`), QMD Pages ('content/').

## Coding Conventions
- **R Scripts:** Syntax: Tidyverse with native `|>` or `%>%` pipes (consistent per file).
- **R Scripts:** Namespace: Prefix non-base functions in snippets (`dplyr::mutate()`, `stringr::str_detect()`).
- **R Scripts:** Naming: Strict `lower_snake_case` for files and objects. No dots in names.
- **R Scripts:** Paths: Relative only via `here::here()`. Never call `setwd()`.
- **R Scripts:** Error Handling: Use `rlang::abort()` / `rlang::warn()`.
- **R Scripts:** Recoverable flows: `purrr::possibly()` for fallbacks, `purrr::safely()` for error logging.
- **R Scripts:** Plotting: `ggplot2` with explicit labels, units, and clean layers.
- **R Scripts:** Dependencies: Managed via `renv`. Snapshot after package additions.
- **Python Scripts:** Use `pandas` and standard scientific library dependencies (`numpy`, `matplotlib`).
- **ObservableJS (`{ojs}`):** Use standard D3, Inputs, or Plot primitives suitable for static Quarto rendering.

## Security & Execution
- Credentials: Never hardcode secrets. Use `Sys.getenv()` or `keyring`.
- Commands & SQL: Parameterized DBI queries only. Use `processx::run()` or `sys::exec_wait()` over `system()`. Avoid `eval(parse())`.
- Inputs & Files: Sanitize with `fs::path_sanitize()`. Validate types and allowlists.

## Reproducibility & Style
- Seeds: Wrap stochastic operations in `withr::with_seed()`.
- Code Chunks: Keep small and focused with explicit options (`echo`, `message`, `warning`).
- Style: Prefer readability, small helper functions, and clear type stability over complex nested pipelines.

  ## Global Quarto & OJS Coding Standards

- **OJS Scope & Reactivity**:
  - Keep all reactive OJS state variables unique across files to prevent cross-page state leaking in Quarto multi-page builds.
  - Avoid using external npm packages unless explicitly required (e.g., dynamic imports via `require()` for SheetJS/Draw.io).
  - Use standard HTML/CSS wrappers (`<div class="card">...</div>`) around OJS inputs and Draw.io controls to maintain clean, scannable layouts.

- **File System & Directory Structure**:
  - **`output/`**: Reserved exclusively for user exports (CSVs, JSONs, `.drawio`, `.svg`, `.png`). Always include helper text prompting the user to place downloaded files here.
  - **`supplement/`**: Reserved for custom schema templates (e.g., `supplement/custom-vsm-schema.json`), helper scripts, or reference documentation.
  - Check that any hardcoded navigation links use relative local paths (e.g., `./process-primary.qmd`).

- **User Guidance & UX**:
  - Every interactive page (`*-primary.qmd`) must start with an instructional callout box (`::: {.callout-note}`) outlining clear step-by-step instructions before the interactive components.
  
  # GitHub Copilot Instructions for `glider-reporter`

## Project Architecture & Core Principles
1. **Open Source & Reproducibility:** All code must be reproducible, well-documented, and cleanly structured in R, Python, or ObservableJS (`{ojs}`).
2. **Client-Side First (GitHub Pages):** All web interactivity (dashboards, field matching, dynamic previewing, and zip bundle downloading) must run entirely client-side using Quarto + ObservableJS (`{ojs}`) or WebAssembly (Pyodide/WebR).
3. **Modular CSS/SCSS Isolation:** Keep styles strictly scoped per dashboard/module using dedicated SCSS files (e.g., `dashboard_builder.scss`, `function_explorer.scss`). Never overwrite global root styles across separate Quarto pages.
4. **Data Standardization & OG1.0 Compliance:**
   - All input datasets must be transformed to `snake_case` for field identifiers.
   - Coordinates MUST be decimal degrees (`float`).
   - Timestamps MUST follow ISO8601 standard (`YYYY-MM-DDTHH:MM:SSZ`).
5. **CORS & GliderDAC / ERDDAP Handling:**
   - Provide clear modal instructions advising users to pre-filter ERDDAP / GliderDAC datasets due to browser CORS and network latency.

## OG1.0 Data Cleaning
- Sample data lives under `data/sample/`; generated examples belong in `data/precomputed_outputs/`.
- Cleaning functions in `python/data_cleaner.py` and `R/data_cleaner.R` normalize headers to `snake_case`, convert coordinates to decimal degrees, and format timestamps as UTC ISO8601.
- Cleaning returns a validation report so missing or malformed `latitude`, `longitude`, and `time` fields are explicit rather than silently ignored.

## Function Registry & Crowd-Sourcing Architecture
1. **GitHub Issue Form Schema:** Function contributions arrive via `.github/ISSUE_TEMPLATE/function_submission.yml`.
2. **Language Ingestion & Polyglot Support:**
   - Primary supported execution languages for reports are `R`, `Python`, and `Quarto`.
   - Contributions are welcome in ANY language (e.g., `MATLAB`, `Julia`, `SAS`, or `Prompt/Pseudo-code`).
   - Submissions outside R, Python, and Quarto are marked with `"translation_status": "needs_translation"` in `functions/registry.json` so community members can adapt them into a supported language.
3. **Registry Standard (`functions/registry.json`):** Every crowd-sourced function must be indexed with: `id`, `name`, `description`, `language`, `translation_status`, `required_fields`, `output_type`, `citation`, `issue_url`, and `code_file`.
4. **Reporting Function Standards:**
   - Standardized functions accept a clean `snake_case` dataframe (from `data_cleaner`).
   - Functions output HTML-renderable plots, Markdown tables, or dynamic summary text.

## Client-Side Data & Field Matching Engine (Quarto + OJS)
1. **Interactive State Management:** Use ObservableJS (`{ojs}`) reactive primitives for client-side state (uploaded file parsing, field matching selections, and validation flags).
2. **Field Matching Persistence:** Enable downloading a JSON/CSV mapping file (`glider_field_mapping.json`) so users can re-use custom field mappings in future reporting sessions.
3. **Data Quality Checks:**
   - Automatically convert latitude/longitude inputs to decimal degrees (`float`).
   - Standardize time fields to ISO8601 strings (`YYYY-MM-DDTHH:MM:SSZ`).
   - If required fields (`latitude`, `longitude`, `time`) fail format checks, display an interactive confirmation prompt that forces user acknowledgment before building reports.
4. **GliderDAC / ERDDAP Modal Guidance:** Display a non-blocking UI alert advising users to pre-filter ERDDAP queries due to browser CORS and network speed constraints.

## Interactive Function Explorer Architecture (`function_explorer.qmd`)
1. **Catalog Rendering:** Dynamically render functions from `functions/registry.json` using ObservableJS (`{ojs}`) inputs (search bar, multi-select dropdowns for required fields, language, and output type).
2. **Slide-Out Metadata Drawer:** Use pure CSS/OJS modal/drawer components defined in `styles/function_explorer.scss` to display detailed function metadata without leaving the page.
3. **Pre-Computed Asset Previews:** Display pre-rendered sample outputs from `data/precomputed_outputs/` in the drawer/cards so users can view expected output figures and tables statically on GitHub Pages.
4. **Issue Link Integration:** Every function card/drawer MUST contain a direct hyperlink to its originating GitHub Issue (`issue_url`), encouraging users to review build history or contribute alternative language versions.
