# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from pathlib import Path

from orcli import Refine

# Create output directory.
output_dir = Path("./temp_output")
output_dir.mkdir(parents=True, exist_ok=True)

input_dir = output_dir / "example04_input"
input_dir.mkdir(parents=True, exist_ok=True)

# Create input files.
input_files = [
    input_dir / "first.csv",
    input_dir / "second.csv",
]

for index, csv_file in enumerate(input_files, start=1):
    csv_file.write_text(
        "name,email,temp_field\n"
        f"Alice{index},ALICE{index}@EXAMPLE.COM,remove1\n"
        f"Bob{index},BOB{index}@EXAMPLE.COM,remove2\n",
        encoding="utf-8",
    )

# Create the operations file.
operations_file = output_dir / "operations_example04.json"
operations_file.write_text(
    json.dumps(
        [
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
    ),
    encoding="utf-8",
)

refine = Refine()

for filename in os.listdir(input_dir):
    if not filename.endswith(".csv"):
        continue

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")

    csv_file = input_dir / filename

    # Save the input state.
    input_output_file = (
        output_dir
        / f"pytest_example04_INPUT_{timestamp}.csv"
    )
    input_output_file.write_text(
        csv_file.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    project_id = refine.create_project(
        project_file=str(csv_file),
        project_name=filename,
    )

    try:
        # Apply the same operations to every project.
        refine.apply_operations_from_file(
            str(operations_file),
            project_id,
            wait=True,
        )

        # Export the final state.
        after_file = (
            output_dir / f"pytest_example04_OUTPUT_{timestamp}.csv"
        )

        refine.export_data(
            str(after_file),
            fmt="csv",
            project_id=project_id,
        )

    finally:
        # Clean up the example project.
        refine.delete_project(project_id)

