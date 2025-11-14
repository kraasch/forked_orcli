# refine-client## Project Overview

This workspace automates OpenRefine project management and data transformation using Python scripts. It interacts with a running OpenRefine server (default: `http://127.0.0.1:3333`) via HTTP API for project creation, operation application, metadata management, and data export.

A comprehensive Python client library for interacting with [OpenRefine](https://openrefine.org/) via its REST API. Simplify project creation, data transformation, metadata management, and export operations.

## Architecture & Major Components

## Features- **Python scripts** 



✨ **Easy Project Management**## Key Workflows

- Create projects from local files (CSV, TSV, JSON, etc.)1. **Start OpenRefine server** (external, not included in repo).

- Delete projects2. **Run a script** to:

- Retrieve project metadata   - Fetch CSRF token

   - Upload `metadata.csv` as a new project

🔄 **Data Transformation**   - Apply operations from `history.json` (can be stepwise in `or2.py`)

- Apply OpenRefine operations (individually or in batches)   - Optionally set project metadata (see `set_project_metadata` in `or2.py`)

- Load operations from JSON files   - Export cleaned data to `exported_data.tsv` (or numbered files in `or2.py`)

- Apply operations with automatic wait-for-idle   - (Optional) Delete or rename project

3. **Debugging**: On error, check `response.html` for details.

📊 **Data Export**

- Export data in multiple formats (TSV, CSV, JSON, etc.)## Project-Specific Conventions & Patterns

- Retrieve column information and project models- All API requests require a valid CSRF token (`csrf_token` parameter). Always fetch before mutating operations.

- Use `requests.Session()` for persistent cookies and headers.

🔐 **Security**- API endpoints use `/command/core/` prefix.

- Automatic CSRF token management and caching- Project ID is parsed from the redirect URL after project creation.

- Session-based authentication- All file paths are relative to the workspace root.

- Error handling with detailed response logging- Error handling: Write failed responses to `response.html` for inspection. See `_save_error_response` 

- Project metadata can be set for fields like `name`, `description`, `creator`, etc. Use `set_project_metadata` 

## Installation

## Integration & Dependencies

### Requirements- Requires a running OpenRefine server (not included in this repo).

- Python 3.10+- Python dependency: `requests` (install via `pip install requests`).

- A running [OpenRefine](https://openrefine.org/) server

## Examples & Usage Patterns

### Setup- To add new operations, edit `history.json` (must be a JSON array of OpenRefine operations).

- To use a different input, replace `metadata.csv`.

1. Clone the repository:- To export as CSV, change the `format` parameter in the export step (see `export_data`).

```bash- To set project metadata, use `set_project_metadata` (see docstring in `or2.py`).

git clone https://github.com/rkraasch/refine-client.git- For stepwise operation and export, see the main block in `or2.py`:

cd refine-client  ```python

```  for operation in data:

      refine.apply_operations([operation])

2. Install dependencies:      refine.export_data(f"exported_data{step}.tsv")

```bash  ```

pip install -r requirements.txt

```## Tips

- If you see `Missing or invalid csrf_token parameter`, ensure the token is fetched and passed correctly.

## Quick Start- For new workflows, use `or1.py` or `or2.py` as the template.

- For debugging, always check `response.html` after errors.

### Basic Usage


```python
from refine_client import Refine

# Initialize the client
refine = Refine(base_url="http://127.0.0.1:3333")

# Create a project
project_id = refine.create_project("data.csv", "My Project")

# Get column names
columns = refine.get_column_names(project_id)
print(f"Columns: {columns}")

# Apply an operation
operation = {
    "op": "core/column-removal",
    "columnName": "unwanted_column",
    "description": "Remove unwanted column"
}
refine.apply_operation(operation, project_id)

# Export data
refine.export_data("output.tsv", fmt="tsv", project_id=project_id)

# Clean up
refine.delete_project(project_id)
```

### Project Metadata

```python
# Set project metadata
refine.set_project_metadata("name", "Updated Project Name", project_id)
refine.set_project_metadata("description", "Project description", project_id)

# Get all projects
projects = refine.get_all_projects_metadata()
for pid, metadata in projects.items():
    print(f"{metadata['name']} (ID: {pid})")

# Find project by name
project_id = refine.get_project_id_by_name("My Project")
```

### Batch Operations

```python
# Apply multiple operations
operations = [
    {"op": "core/column-removal", "columnName": "col1"},
    {"op": "core/column-removal", "columnName": "col2"}
]
refine.apply_operations(operations, project_id)

# Load operations from file
refine.apply_operations_from_file("operations.json", project_id, wait=True)
```

### Advanced: Wait for Completion

```python
# Apply operation and wait for completion
refine.apply_operation(operation, project_id, wait=True)

# Or manually wait
refine.wait_until_idle(project_id)
```

## API Reference

### Initialization

```python
Refine(base_url=None, verbose=False, silent=False)
```

**Parameters:**
- `base_url` (str, optional): OpenRefine server URL (default: `http://127.0.0.1:3333`)
- `verbose` (bool): Enable verbose logging
- `silent` (bool): Suppress logging output

### Project Management

| Method | Description |
|--------|-------------|
| `create_project(file, name)` | Create a new project from file |
| `delete_project(project_id)` | Delete a project |
| `get_all_projects_metadata()` | Get metadata for all projects |
| `get_project_id_by_name(name)` | Find project ID by name |
| `set_project_metadata(field, value, project_id)` | Update project metadata |

### Operations

| Method | Description |
|--------|-------------|
| `apply_operation(op, project_id, wait=False)` | Apply single operation |
| `apply_operations(ops, project_id, wait=False)` | Apply multiple operations |
| `apply_operations_from_file(file, project_id, wait=False)` | Load and apply operations from JSON |

### Data Retrieval

| Method | Description |
|--------|-------------|
| `get_models(project_id)` | Get project models |
| `get_column_names(project_id)` | Get column names |
| `export_data(file, fmt, project_id)` | Export project data |
| `rows_as_list(data)` | Convert rows to list format |

### Utility

| Method | Description |
|--------|-------------|
| `wait_until_idle(project_id, delay=0.5)` | Wait for processing to complete |

## Configuration

### Logging

Control logging output:

```python
# Verbose mode (debug level)
refine = Refine(verbose=True)

# Silent mode (errors only)
refine = Refine(silent=True)
```

### Custom Base URL

```python
# For remote OpenRefine servers
refine = Refine(base_url="http://example.com:3333")
```

## Error Handling

The client automatically saves error responses to `response.html` for debugging:

```python
try:
    refine.apply_operation(operation, project_id)
except RuntimeError as e:
    print(f"Error: {e}")
    print("Check response.html for details")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest Test/ -v

# Run specific test class
pytest Test/test_refine_client.py::TestRefineProjectCreation -v

# Run with coverage
pytest Test/ --cov=refine_client
```

**Test Coverage:**
- ✅ Initialization and connection handling
- ✅ CSRF token management
- ✅ Project creation and deletion
- ✅ Operations (single, batch, from file)
- ✅ Data export
- ✅ Metadata management
- ✅ Error handling

## Examples

### Example 1: Data Cleaning Pipeline

```python
from refine_client import Refine

refine = Refine(verbose=True)

# Create project
project_id = refine.create_project("raw_data.csv", "Data Cleanup")

# Apply cleaning operations
operations = [
    {"op": "core/column-removal", "columnName": "temporary_id"},
    {"op": "core/text-transform", "columnName": "email", "expression": "value.toLowerCase()"}
]
refine.apply_operations(operations, project_id, wait=True)

# Export cleaned data
refine.export_data("cleaned_data.csv", fmt="csv", project_id=project_id)

# Cleanup
refine.delete_project(project_id)
```

### Example 2: Batch Processing

```python
import os
from refine_client import Refine

refine = Refine()

# Process multiple files
for filename in os.listdir("data/"):
    if filename.endswith(".csv"):
        project_id = refine.create_project(f"data/{filename}", filename)
        
        # Apply transformations
        refine.apply_operations_from_file("transformations.json", project_id, wait=True)
        
        # Export
        base_name = os.path.splitext(filename)[0]
        refine.export_data(f"output/{base_name}_cleaned.csv", fmt="csv", project_id=project_id)
        
        # Cleanup
        refine.delete_project(project_id)
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionError: Could not connect to OpenRefine server`

**Solution:**
1. Ensure OpenRefine is running: `http://127.0.0.1:3333`
2. Check the server URL: `refine = Refine(base_url="http://your-server:3333")`
3. Verify network connectivity

### CSRF Token Errors

**Problem:** `ValueError: CSRF token retrieval failed`

**Solution:**
- The token is automatically fetched. This usually indicates server issues.
- Check `response.html` for details

### File Not Found

**Problem:** `FileNotFoundError: File not found`

**Solution:**
- Use absolute paths or ensure files are in the working directory
- Check file permissions

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the CC0 1.0 Universal License - see the LICENSE file for details.

## References

- [OpenRefine Official Documentation](https://docs.openrefine.org/)
- [OpenRefine REST API](https://docs.openrefine.org/manual/running#command-line-interface)
- [OpenRefine Operations](https://docs.openrefine.org/manual/running#command-line-interface)

## Changelog

### v1.0.0 (2025-11-14)
- ✅ Initial release
- ✅ Full project management support
- ✅ Operation batching
- ✅ Comprehensive test suite (33 tests)
- ✅ CI/CD integration with GitHub Actions

## Support

For issues, questions, or suggestions, please open an [issue](https://github.com/rkraasch/refine-client/issues) on GitHub.
