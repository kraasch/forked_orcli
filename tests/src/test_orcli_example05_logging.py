# -*- coding: utf-8 -*-

import logging
import sys
import unittest
from datetime import datetime
from pathlib import Path
import tempfile

sys.path.insert(
    0,
    str(Path(__file__).parent.parent),
)  # Add parent directory to path to import orcli.

import orcli.client
from orcli import Refine


class TestExample05Logging(unittest.TestCase):

    def setUp(self):
        """Configure a dedicated logging handler for each test."""

        # Save the global logging disable level.
        self.original_disable_level = logging.root.manager.disable

        # Previous tests disable logging globally with
        # logging.disable(logging.CRITICAL). Re-enable logging
        # for these logging tests.
        logging.disable(logging.NOTSET)

        # Use the exact logger used by client.py:
        #
        #     logger = logging.getLogger(__name__)
        #
        self.logger = orcli.client.logger

        self.original_level = self.logger.level
        self.original_propagate = self.logger.propagate

        self.log_records = []

        class ListHandler(logging.Handler):
            def __init__(self, records):
                super().__init__()
                self.records = records

            def emit(self, record):
                self.records.append(record)

        self.handler = ListHandler(self.log_records)

        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def tearDown(self):
        """Restore the original logger configuration."""

        self.logger.removeHandler(self.handler)
        self.logger.setLevel(self.original_level)
        self.logger.propagate = self.original_propagate

        # Restore the global logging disable level used before
        # this test.
        logging.disable(self.original_disable_level)

    def _set_log_level(self, level):
        """Set the logging level used by the test."""
        self.logger.setLevel(level)
        self.log_records.clear()

    def _messages(self):
        """Return captured log messages."""
        return [
            record.getMessage()
            for record in self.log_records
        ]

    def test_debug_logging(self):
        """DEBUG logging should include DEBUG, INFO and higher messages."""

        self._set_log_level(logging.DEBUG)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / (
                f"logging_debug_{timestamp}.csv"
            )

            csv_file.write_text(
                "name,age\n"
                "Alice,30\n"
                "Bob,25\n",
                encoding="utf-8",
            )

            refine = Refine()

            try:
                project_id = refine.create_project(
                    project_file=str(csv_file),
                    project_name=f"Logging DEBUG {timestamp}",
                )

                refine.get_models(project_id)

            finally:
                if refine.project_id:
                    refine.delete_project(refine.project_id)

        messages = self._messages()

        self.assertTrue(messages)

        # DEBUG messages should be present.
        self.assertTrue(
            any(
                "CSRF token retrieved successfully." in message
                for message in messages
            )
        )

        # INFO messages should also be present.
        self.assertTrue(
            any(
                "Project created successfully" in message
                for message in messages
            )
        )

        self.assertTrue(
            any(
                "Get models" in message
                for message in messages
            )
        )

        # Deletion is also logged at INFO level.
        self.assertTrue(
            any(
                "Deleted project" in message
                for message in messages
            )
        )

        # Verify that DEBUG records are actually captured.
        self.assertTrue(
            any(
                record.levelno == logging.DEBUG
                for record in self.log_records
            )
        )

    def test_info_logging(self):
        """INFO logging should include INFO and higher messages,
        but not DEBUG.
        """

        self._set_log_level(logging.INFO)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / (
                f"logging_info_{timestamp}.csv"
            )

            csv_file.write_text(
                "name,age\n"
                "Alice,30\n"
                "Bob,25\n",
                encoding="utf-8",
            )

            refine = Refine()

            try:
                refine.create_project(
                    project_file=str(csv_file),
                    project_name=f"Logging INFO {timestamp}",
                )

            finally:
                if refine.project_id:
                    refine.delete_project(refine.project_id)

        messages = self._messages()

        self.assertTrue(messages)

        # INFO messages should be present.
        self.assertTrue(
            any(
                "Connected to OpenRefine server" in message
                for message in messages
            )
        )

        self.assertTrue(
            any(
                "Project created successfully" in message
                for message in messages
            )
        )

        self.assertTrue(
            any(
                "Deleted project" in message
                for message in messages
            )
        )

        # DEBUG messages must not be emitted at INFO level.
        self.assertFalse(
            any(
                record.levelno == logging.DEBUG
                for record in self.log_records
            )
        )

    def test_warning_logging(self):
        """WARNING logging should suppress INFO and DEBUG messages."""

        self._set_log_level(logging.WARNING)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_file = Path(tmp_dir) / (
                f"logging_warning_{timestamp}.csv"
            )

            csv_file.write_text(
                "name,age\n"
                "Alice,30\n"
                "Bob,25\n",
                encoding="utf-8",
            )

            refine = Refine()

            try:
                refine.create_project(
                    project_file=str(csv_file),
                    project_name=f"Logging WARNING {timestamp}",
                )

            finally:
                if refine.project_id:
                    refine.delete_project(refine.project_id)

        # Refine currently does not emit WARNING messages during
        # a successful workflow.
        self.assertEqual(self.log_records, [])

    def test_error_logging(self):
        """ERROR logging should contain errors and suppress
        INFO and DEBUG.
        """

        self._set_log_level(logging.ERROR)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_file = (
                Path(tmp_dir) / "does_not_exist.csv"
            )

            refine = Refine()

            with self.assertRaises(FileNotFoundError):
                refine.create_project(
                    project_file=str(missing_file),
                    project_name=f"Logging ERROR {timestamp}",
                )

        messages = self._messages()

        self.assertTrue(messages)

        # The missing file should produce an ERROR log.
        self.assertTrue(
            any(
                "File not found" in message
                for message in messages
            )
        )

        # INFO and DEBUG records must not pass the ERROR threshold.
        self.assertFalse(
            any(
                record.levelno < logging.ERROR
                for record in self.log_records
            )
        )


if __name__ == "__main__":
    unittest.main()

