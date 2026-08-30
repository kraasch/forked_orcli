# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path

from orcli import Refine


# Create output directory.
output_dir = Path("./temp_output")
output_dir.mkdir(parents=True, exist_ok=True)

# Create input data.
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

csv_file = output_dir / f"pytest_example03_INPUT_{timestamp}.csv"
csv_file.write_text(
    "name,email,temp_field\n"
    "Alice,ALICE@EXAMPLE.COM,remove1\n"
    "Bob,BOB@EXAMPLE.COM,remove2\n",
    encoding="utf-8",
)

project_name = (
    f"Project Name Test Example 03_{timestamp}"
)

refine = Refine(verbose=True)

try:
    # Create project.
    project_id = refine.create_project(
        project_file=str(csv_file),
        project_name=project_name,
    )

    # Transform data.
    operations = [
        {
            "op": "core/column-removal",
            "columnName": "temp_field",
        },
        {
            "op": "core/text-transform",
            "engineConfig": {
                "facets": [],
                "mode": "row-based",
            },
            "columnName": "email",
            "expression": "value.toLowercase()",
            "onError": "keep-original",
            "repeat": False,
            "repeatCount": 10,
        },
    ]

    refine.apply_operations(
        operations,
        project_id,
        wait=True,
    )

    # Export the final state.
    after_file = output_dir / f"pytest_example03_OUTPUT_{timestamp}.csv"
    refine.export_data(
        str(after_file),
        fmt="csv",
        project_id=project_id,
    )

finally:
    # Clean up the example project.
    if refine.project_id:
        refine.delete_project(refine.project_id)
