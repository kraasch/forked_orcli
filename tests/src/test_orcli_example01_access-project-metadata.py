# -*- coding: utf-8 -*-

import unittest
import logging
import sys
from datetime import datetime
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent)) # Add parent directory to path to import orcli.

from orcli import Refine

logging.disable(logging.CRITICAL) # Disable logging during tests.

class TestExample01AccessProjectMetadata(unittest.TestCase):

    def test_access_project_metadata(self):
        """Access and modify project metadata."""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Create a temporary directory for the CSV file.
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / f"pytest_data_{timestamp}.csv"
            csv_file.write_text(
                "name,age\nAlice,30\nBob,25\n",
                encoding="utf-8",
            )
            # Create unique project names.
            original_project_name = (
                f"pytest_refine-client-integration_{timestamp}"
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
                self.assertTrue(project_id)
                self.assertEqual(refine.project_id, project_id)
                # Get all project metadata.
                projects = refine.get_all_projects_metadata()
                self.assertIn(project_id, projects)
                self.assertEqual(
                    projects[project_id]["name"],
                    original_project_name,
                )
                # Find the project ID by its name.
                found_project_id = refine.get_project_id_by_name(
                    original_project_name
                )
                self.assertEqual(found_project_id, project_id)
                # Change the project name.
                refine.set_project_metadata(
                    "name",
                    updated_project_name,
                    project_id,
                )
                # Read the metadata again.
                projects = refine.get_all_projects_metadata()
                self.assertIn(project_id, projects)
                self.assertEqual(
                    projects[project_id]["name"],
                    updated_project_name,
                )
                # Verify the project can be found by its new name.
                found_project_id = refine.get_project_id_by_name(
                    updated_project_name
                )
                self.assertEqual(found_project_id, project_id)
                # Print all projects.
                for pid, metadata in projects.items():
                    print(f"{metadata['name']} (ID: {pid})")
            finally:
                # Clean up the test project.
                if refine.project_id:
                    refine.delete_project(refine.project_id)

if __name__ == "__main__":
    unittest.main()

