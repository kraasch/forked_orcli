# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path

from orcli import Refine


# Create output directory.
output_dir = Path("./temp_output")
output_dir.mkdir(parents=True, exist_ok=True)

# Create input data.
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

csv_file = output_dir / f"pytest_example01_INPUT_{timestamp}.csv"
csv_file.write_text(
    "name,age\n"
    "Alice,30\n"
    "Bob,25\n",
    encoding="utf-8",
)

# Create unique project names.
original_project_name = (
    f"Project Name Test Example 01 REMOVE THIS FROM THE NAME {timestamp}"
)
updated_project_name = (
    f"Project Name Test Example 01_{timestamp}"
)

refine = Refine()

try:
    # Create the project.
    project_id = refine.create_project(
        project_file=str(csv_file),
        project_name=original_project_name,
    )

    # Get all projects.
    projects = refine.get_all_projects_metadata()
    for pid, metadata in projects.items():
        print(f"{metadata['name']} (ID: {pid})")

    # Find the project ID by its name.
    found_project_id = refine.get_project_id_by_name(
        original_project_name
    )
    print(f"Found project ID: {found_project_id}")

    # Change the project name.
    refine.set_project_metadata(
        "name",
        updated_project_name,
        project_id,
    )

    # Get all projects again.
    projects = refine.get_all_projects_metadata()
    for pid, metadata in projects.items():
        print(f"{metadata['name']} (ID: {pid})")

    # Find the project ID by its new name.
    found_project_id = refine.get_project_id_by_name(
        updated_project_name
    )
    print(f"Found project ID: {found_project_id}")

    # Export the final state.
    after_file = output_dir / f"pytest_example01_OUTPUT_{timestamp}.csv"
    refine.export_data(
        str(after_file),
        fmt="csv",
        project_id=project_id,
    )

finally:
    # Clean up the example project.
    if refine.project_id:
        refine.delete_project(refine.project_id)

