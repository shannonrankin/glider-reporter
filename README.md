# glider-reporter
Reproducible template (in development) for creating reproducible reports for underwater oceanographic gliders

Function metadata is stored in `functions/*.md` YAML frontmatter. Run
`python -m pip install -r requirements.txt` and `python functions/build_registry.py`
after adding or editing a function to regenerate `functions/registry.json`.
