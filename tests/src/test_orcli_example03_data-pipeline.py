# -*- coding: utf-8 -*-

import unittest
import logging
import sys
from datetime import datetime
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))  # Add parent directory to path to import orcli.

from orcli import Refine

logging.disable(logging.CRITICAL)  # Disable logging during tests.


class TestExample03DataPipeline(unittest.TestCase):

    def test_data_pipeline(self):
        """Create a project, transform data, export it and clean up."""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            csv_file = tmp_path / f"raw_data_{timestamp}.csv"
            csv_file.write_text(
                "name,email,temp_field\n"
                "Alice,ALICE@EXAMPLE.COM,remove1\n"
                "Bob,BOB@EXAMPLE.COM,remove2\n",
                encoding="utf-8",
            )

            output_file = tmp_path / f"processed_data_{timestamp}.csv"

            project_name = (
                f"pytest_orcli-integration_example03_{timestamp}"
            )

            refine = Refine(verbose=True)

            try:
                # Create project.
                project_id = refine.create_project(
                    project_file=str(csv_file),
                    project_name=project_name,
                )

                self.assertTrue(project_id)
                self.assertEqual(refine.project_id, project_id)

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

                # Export the processed project.
                refine.export_data(
                    str(output_file),
                    fmt="csv",
                    project_id=project_id,
                )

                # Verify that the export was created.
                self.assertTrue(output_file.exists())
                self.assertGreater(output_file.stat().st_size, 0)

                # Verify the exported data.
                exported_data = output_file.read_text(
                    encoding="utf-8"
                )

                self.assertIn("name,email", exported_data)

                # Verify that the temporary column was removed.
                self.assertNotIn("temp_field", exported_data)

                # Verify that the email values were converted to lowercase.
                self.assertIn(
                    "Alice,alice@example.com",
                    exported_data,
                )
                self.assertIn(
                    "Bob,bob@example.com",
                    exported_data,
                )

                # Verify that the uppercase values are no longer present.
                self.assertNotIn(
                    "ALICE@EXAMPLE.COM",
                    exported_data,
                )
                self.assertNotIn(
                    "BOB@EXAMPLE.COM",
                    exported_data,
                )

            finally:
                # Clean up the test project.
                if refine.project_id:
                    refine.delete_project(refine.project_id)


if __name__ == "__main__":
    unittest.main()

