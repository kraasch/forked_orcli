# -*- coding: utf-8 -*-

import unittest
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))  # Add parent directory to path to import orcli.

from orcli import Refine

logging.disable(logging.CRITICAL)  # Disable logging during tests.


class TestExample04BatchProcessing(unittest.TestCase):

    def test_batch_processing(self):
        """Process multiple CSV files using the same operations file."""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            input_dir = tmp_path / "input_dir"
            output_dir = tmp_path / "output_dir"

            input_dir.mkdir()
            output_dir.mkdir()

            # Create multiple input CSV files.
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

            # Create the operations file used for every project.
            operations_file = tmp_path / "operations.json"
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
            created_project_ids = []

            try:
                # Process every CSV file in the input directory.
                for index, filename in enumerate(
                    sorted(input_dir.iterdir()),
                    start=1,
                ):
                    if filename.suffix != ".csv":
                        continue

                    project_id = refine.create_project(
                        project_file=str(filename),
                        project_name=filename.name,
                    )

                    self.assertTrue(project_id)
                    created_project_ids.append(project_id)

                    # Apply the operations from the file.
                    refine.apply_operations_from_file(
                        str(operations_file),
                        project_id,
                        wait=True,
                    )

                    # Export the processed project.
                    output_file = output_dir / filename.name

                    refine.export_data(
                        str(output_file),
                        fmt="csv",
                        project_id=project_id,
                    )

                    # export_data() returns None, so verify the file.
                    self.assertTrue(output_file.exists())
                    self.assertGreater(output_file.stat().st_size, 0)

                    # Verify the exported data.
                    exported_data = output_file.read_text(
                        encoding="utf-8"
                    )

                    self.assertIn("name,email", exported_data)

                    # Verify that the temporary column was removed.
                    self.assertNotIn("temp_field", exported_data)

                    # Verify that the email values were converted
                    # to lowercase.
                    self.assertIn(
                        f"Alice{index},alice{index}@example.com",
                        exported_data,
                    )
                    self.assertIn(
                        f"Bob{index},bob{index}@example.com",
                        exported_data,
                    )

                    # Verify that the uppercase values are gone.
                    self.assertNotIn(
                        f"ALICE{index}@EXAMPLE.COM",
                        exported_data,
                    )
                    self.assertNotIn(
                        f"BOB{index}@EXAMPLE.COM",
                        exported_data,
                    )

                    # Match the README example: delete the project
                    # after processing it.
                    refine.delete_project(project_id)

                # Verify that every input file produced an output file.
                output_files = sorted(output_dir.glob("*.csv"))

                self.assertEqual(
                    len(output_files),
                    len(input_files),
                )

                self.assertEqual(
                    {file.name for file in output_files},
                    {file.name for file in input_files},
                )

            finally:
                # Clean up any projects that were not deleted during
                # normal processing.
                for project_id in created_project_ids:
                    try:
                        refine.delete_project(project_id)
                    except Exception:
                        pass


if __name__ == "__main__":
    unittest.main()

