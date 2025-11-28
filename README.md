# refine-client

A comprehensive Python client library for interacting with [OpenRefine](https://openrefine.org/) via its REST API.

Simplify project creation, data transformation, metadata management, and export operations.

## Features

### Easy Project Management

- Create projects from local files
- Delete projects
- Retrieve and manage project metadata

### Data Transformation

- Apply OpenRefine operations individually or in batches
- Load operations from JSON files
- Automatic wait-for-idle synchronization

### Data Export

- Export data in multiple formats (TSV, CSV, JSON, etc.)
- Retrieve column information and project models
- Convert and manipulate row data

### Security & Reliability

- Automatic CSRF token management and caching
- Session-based authentication
- Error handling with detailed response logging

## Installation

### Requirements

- Python 3.10+
- A running OpenRefine server instance

### Setup

1. Clone the repository:

```bash
git clone https://github.com/rkraasch/refine-client.git
cd refine-client
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

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

### Project Metadata

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

### Batch Operations

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

## Error Handling

```python
try:
    refine.apply_operation(operation, project_id)
except RuntimeError as e:
    print(f"Error: {e}")
```

## Testing

```bash
# Run all tests
pytest Test/ -v

# Run specific test
pytest Test/test_refine_client.py::TestRefineProjectCreation -v

# With coverage
pytest Test/ --cov=refine_client
```

Test Coverage:
- Initialization and connection
- CSRF token management
- Project operations
- Batch operations
- Data export
- Metadata management
- Error handling

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

## Troubleshooting

### Connection Issues

Problem: ConnectionError

Solution:
1. Verify OpenRefine is running
2. Check server URL
3. Verify network connectivity

### CSRF Token Errors

Problem: ValueError: CSRF token retrieval failed

Solution:
- Usually indicates server issues
- Check server logs

### File Not Found

Problem: FileNotFoundError

Solution:
- Use absolute paths
- Verify file exists
- Check permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## License

CC0 1.0 Universal License

## References

- [OpenRefine Documentation](https://docs.openrefine.org/)
- [OpenRefine REST API](https://docs.openrefine.org/manual/running)
- [OpenRefine Operations](https://docs.openrefine.org/manual/running)

## Changelog

### v1.0.0 (2025-11-14)

- Initial release
- Full project management
- Operation batching
- 33 comprehensive tests
- GitHub Actions CI/CD

## Support

Open an issue on [GitHub](https://github.com/rkraasch/refine-client/issues)
