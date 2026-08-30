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


class TestExample02BatchOperations(unittest.TestCase):

    def test_batch_operations(self):
        """Apply multiple operations and load operations from a file."""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            csv_file = tmp_path / f"pytest_data_{timestamp}.csv"
            csv_file.write_text(
                "name,age,temp1,temp2\n"
                "Alice,30,remove1,remove2\n"
                "Bob,25,remove3,remove4\n",
                encoding="utf-8",
            )

            operations_file = tmp_path / "operations.json"
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
                f"pytest_orcli-integration_example02_{timestamp}"
            )

            refine = Refine()

            try:
                # Create the project.
                project_id = refine.create_project(
                    project_file=str(csv_file),
                    project_name=project_name,
                )

                self.assertTrue(project_id)
                self.assertEqual(refine.project_id, project_id)

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

                result = refine.apply_operations(
                    operations,
                    project_id,
                    wait=True,
                )

                # The operation should complete without raising an exception.
                self.assertIsNotNone(result)

                # Create a second project for testing operations loaded
                # from a file.
                second_project_name = (
                    f"pytest_orcli-integration_example02_file_{timestamp}"
                )

                second_project_id = refine.create_project(
                    project_file=str(csv_file),
                    project_name=second_project_name,
                )

                self.assertTrue(second_project_id)

                try:
                    result = refine.apply_operations_from_file(
                        str(operations_file),
                        second_project_id,
                        wait=True,
                    )

                    # The operation should complete without raising an exception.
                    self.assertIsNotNone(result)

                finally:
                    # Clean up the second test project.
                    if refine.project_id == second_project_id:
                        refine.delete_project(second_project_id)

                    else:
                        refine.delete_project(second_project_id)

            finally:
                # Clean up the first test project.
                if refine.project_id == project_id:
                    refine.delete_project(project_id)

                else:
                    # The current project may have changed while testing
                    # the second project.
                    try:
                        refine.delete_project(project_id)
                    except Exception:
                        pass


if __name__ == "__main__":
    unittest.main()

