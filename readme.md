## Project Overview
This workspace automates OpenRefine project management and data transformation using Python scripts. It interacts with a running OpenRefine server (default: `http://127.0.0.1:3333`) via HTTP API for project creation, operation application, metadata management, and data export.

## Architecture & Major Components
- **Python scripts** 

## Key Workflows
1. **Start OpenRefine server** (external, not included in repo).
2. **Run a script** to:
   - Fetch CSRF token
   - Upload `metadata.csv` as a new project
   - Apply operations from `history.json` (can be stepwise in `or2.py`)
   - Optionally set project metadata (see `set_project_metadata` in `or2.py`)
   - Export cleaned data to `exported_data.tsv` (or numbered files in `or2.py`)
   - (Optional) Delete or rename project
3. **Debugging**: On error, check `response.html` for details.

## Project-Specific Conventions & Patterns
- All API requests require a valid CSRF token (`csrf_token` parameter). Always fetch before mutating operations.
- Use `requests.Session()` for persistent cookies and headers.
- API endpoints use `/command/core/` prefix.
- Project ID is parsed from the redirect URL after project creation.
- All file paths are relative to the workspace root.
- Error handling: Write failed responses to `response.html` for inspection. See `_save_error_response` 
- Project metadata can be set for fields like `name`, `description`, `creator`, etc. Use `set_project_metadata` 

## Integration & Dependencies
- Requires a running OpenRefine server (not included in this repo).
- Python dependency: `requests` (install via `pip install requests`).

## Examples & Usage Patterns
- To add new operations, edit `history.json` (must be a JSON array of OpenRefine operations).
- To use a different input, replace `metadata.csv`.
- To export as CSV, change the `format` parameter in the export step (see `export_data`).
- To set project metadata, use `set_project_metadata` (see docstring in `or2.py`).
- For stepwise operation and export, see the main block in `or2.py`:
  ```python
  for operation in data:
      refine.apply_operations([operation])
      refine.export_data(f"exported_data{step}.tsv")
  ```

## Tips
- If you see `Missing or invalid csrf_token parameter`, ensure the token is fetched and passed correctly.
- For new workflows, use `or1.py` or `or2.py` as the template.
- For debugging, always check `response.html` after errors.

