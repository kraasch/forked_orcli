
# refine-client

A Python client library for interacting with [OpenRefine](https://openrefine.org/) via its REST API.
For simple project creation, data transformation, metadata management and export operations.

## Features

  - Create and delete projects from local files.
  - Retrieve and manage project metadata.
  - Apply OpenRefine operations individually or in batches.
  - Load operations from JSON files.
  - Export data in multiple formats (TSV, CSV, JSON).
  - Retrieve column information and project models, convert and manipulate row data.
  - Error handling with detailed response logging.

## Installation

### Requirements

Requires Python 3.10+ and a running OpenRefine server instance.

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/rkraasch/refine-client.git
cd refine-client
```

2. Install dependencies:

```bash
python -m venv .venv
source [.venv/bin/activate](.venv/bin/activate)  # Linux and Mac.
# .venv\Scripts\activate   # Windows.
pip install -r requirements.txt
python -m pip list
deactivate
```

3. Optionally run tests:

[Download](https://openrefine.org/download) and run OpenRefine, then run the tests as shown below.

```bash
python -m pytest tests/ -v
```

This creates a temporary test project inside OpenRefine which should be cleaned up automatically if everything works as expected.
The test project will be called `pytest_refine-client-integration_` with a timestamp at the end, if you see it in the `Open project` tab of your [OpenRefine instance](http://127.0.0.1:3333/#open-project) something went wrong.

4. Basic Usage:

```python
from refine_client import Refine

# Initialize the client
refine = Refine(base_url="http://127.0.0.1:3333")

# Create a project
project_id = refine.create_project("input_file.csv", "My Project")

# Get column names
columns = refine.get_column_names(project_id)
print(f"Columns: {columns}")

# Apply an operation
operation = {
    "op": "core/column-removal",
    "columnName": "unwanted_column",
    "description": "Remove column"
}
refine.apply_operation(operation, project_id)

# Export data
refine.export_data("output_file.tsv", fmt="tsv", project_id=project_id)

# Clean up
refine.delete_project(project_id)
```

5. Access Project Metadata:

```python
# Set metadata
refine.set_project_metadata("name", "Project Name", project_id)

# Get all projects
projects = refine.get_all_projects_metadata()
for pid, metadata in projects.items():
    print(f"{metadata['name']} (ID: {pid})")

# Find by name
project_id = refine.get_project_id_by_name("Project Name")
```

6. Do Batch Operations:

```python
# Apply multiple operations
operations = [
    {"op": "core/column-removal", "columnName": "col1"},
    {"op": "core/column-removal", "columnName": "col2"}
]
refine.apply_operations(operations, project_id)

# Load from file
refine.apply_operations_from_file("operations.json", project_id, wait=True)
```

## Examples

### Example 1: Data Pipeline

```python
from refine_client import Refine

refine = Refine(verbose=True)

# Create project
project_id = refine.create_project("raw_data.csv", "Processing")

# Transform data
operations = [
    {"op": "core/column-removal", "columnName": "temp_field"},
    {"op": "core/text-transform", "columnName": "email",
     "expression": "value.toLowerCase()"}
]
refine.apply_operations(operations, project_id, wait=True)

# Export
refine.export_data("processed_data.csv", fmt="csv", project_id=project_id)

# Cleanup
refine.delete_project(project_id)
```

### Example 2: Batch Processing

```python
import os
from refine_client import Refine

refine = Refine()

for filename in os.listdir("input_dir/"):
    if filename.endswith(".csv"):
        project_id = refine.create_project(f"input_dir/{filename}", filename)
        refine.apply_operations_from_file("operations.json", project_id, wait=True)
        refine.export_data(f"output_dir/{filename}", fmt="csv", project_id=project_id)
        refine.delete_project(project_id)
```

## API Reference

### Initialization

```python
Refine(base_url=None, verbose=False, silent=False)
```

Parameters:
- base_url: OpenRefine server URL (default: http://127.0.0.1:3333)
- verbose: Enable verbose logging
- silent: Suppress logging

### Methods

| Method | Description |
|--------|-------------|
| create_project(file, name) | Create project |
| delete_project(project_id) | Delete project |
| get_all_projects_metadata() | Get all projects |
| get_project_id_by_name(name) | Find project by name |
| set_project_metadata(field, value, id) | Update metadata |
| apply_operation(op, id, wait) | Apply operation |
| apply_operations(ops, id, wait) | Apply multiple |
| apply_operations_from_file(file, id, wait) | Load from file |
| get_models(id) | Get models |
| get_column_names(id) | Get columns |
| export_data(file, fmt, id) | Export data |
| rows_as_list(data) | Convert rows |
| wait_until_idle(id, delay) | Wait for completion |

## Configuration

### Logging

```python
# Verbose mode
refine = Refine(verbose=True)

# Silent mode
refine = Refine(silent=True)
```

### Custom Server

```python
refine = Refine(base_url="http://example.com:3333")
```

## Troubleshooting

  - **ConnectionError:** Ensure OpenRefine is running, verify the server URL and check network connectivity.
  - **CSRF token errors:** Check server status and logs.
  - **FileNotFoundError:** Use absolute paths, verify the file exists and check permissions.

## Support and Contribute

Open an issue on the project's [issues tab](https://github.com/rkraasch/refine-client/issues) on Github.

Or contribute via Github:

  - fork the repository,
  - create a feature branch,
  - commit changes,
  - push to branch,
  - open Pull Request.

## References

References:

  - [OpenRefine Documentation](https://docs.openrefine.org/)
  - [OpenRefine REST API](https://docs.openrefine.org/manual/running)

Similar Projects:

  - [paulmakepeace/refine-client-py](https://github.com/paulmakepeace/refine-client-py): OpenRefine Python 2 Client (last update 11 years ago).
  - [opencultureconsulting/openrefine-client](https://github.com/opencultureconsulting/openrefine-client): OpenRefine Python Client (archived 2024).

## License

This project is released under [CC0 1.0 Universal License](https://creativecommons.org/publicdomain/zero/1.0/).
For a plain text version see this project's [LICENSE file](./LICENSE.md) or visit [creativecommons.org](https://creativecommons.org/2011/04/15/plaintext-versions-of-creative-commons-licenses-and-cc0/).

