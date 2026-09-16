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



