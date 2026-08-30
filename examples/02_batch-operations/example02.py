# -*- coding: utf-8 -*-

import json
from datetime import datetime
from pathlib import Path

from orcli import Refine

# Create output directory.
output_dir = Path("./temp_output")
output_dir.mkdir(parents=True, exist_ok=True)

# Create input data.
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

csv_file = output_dir / f"pytest_example02_INPUT_data_{timestamp}.csv"
csv_file.write_text(
    "name,age,temp1,temp2\n"
    "Alice,30,remove1,remove2\n"
    "Bob,25,remove3,remove4\n",
    encoding="utf-8",
)

# Create the operations file.
operations_file = output_dir / f"pytest_example02_INPUT_ops_{timestamp}.json"
operations_file.write_text(
    json.dumps(
        [
            {
                "op": "core/column-removal",
                "columnName": "temp1",
            },
            {
                "op": "core/column-removal",
                "columnName": "temp2",
            },
        ]
    ),
    encoding="utf-8",
)

project_name = (
    f"Project Name Test Example 02_{timestamp}"
)

refine = Refine()

try:
    # Create the project.
    project_id = refine.create_project(
        project_file=str(csv_file),
        project_name=project_name,
    )

    # Apply multiple operations directly.
    operations = [
        {
            "op": "core/column-removal",
            "columnName": "temp1",
        },
        {
            "op": "core/column-removal",
            "columnName": "temp2",
        },
    ]

    refine.apply_operations(
        operations,
        project_id,
        wait=True,
    )

    # Export the final state.
    after_file = output_dir / f"pytest_example02_OUTPUT_{timestamp}.csv"
    refine.export_data(
        str(after_file),
        fmt="csv",
        project_id=project_id,
    )

    # Create a second project to demonstrate loading operations
    # from a file.
    second_project_name = (
        f"Project Name Test Example 02 File_{timestamp}"
    )

    second_project_id = refine.create_project(
        project_file=str(csv_file),
        project_name=second_project_name,
    )

    try:
        refine.apply_operations_from_file(
            str(operations_file),
            second_project_id,
            wait=True,
        )
    finally:
        refine.delete_project(second_project_id)

finally:
    # Clean up the first example project.
    if refine.project_id:
        refine.delete_project(refine.project_id)

