# -*- coding: utf-8 -*-
# test_refine_client.py
# Unit tests for refine_client.py

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

# Add parent directory to path to import refine_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.refine_client import Refine


class TestRefineInitialization(unittest.TestCase):
    """Test cases for Refine class initialization."""

    @patch('refine_client.requests.Session')
    def test_init_default_url(self, mock_session_class):
        """Test initialization with default URL."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        self.assertEqual(refine.base_url, "http://127.0.0.1:3333")
        self.assertIsNone(refine.project_id)
        self.assertFalse(refine.silent)
        self.assertFalse(refine.verbose)

    @patch('refine_client.requests.Session')
    def test_init_custom_url(self, mock_session_class):
        """Test initialization with custom URL."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine(base_url="http://example.com:3333")
        self.assertEqual(refine.base_url, "http://example.com:3333")

    @patch('refine_client.requests.Session')
    def test_init_url_trailing_slash_removed(self, mock_session_class):
        """Test that trailing slashes are removed from base_url."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine(base_url="http://example.com:3333/")
        self.assertEqual(refine.base_url, "http://example.com:3333")

    @patch('refine_client.requests.Session')
    def test_init_connection_failure(self, mock_session_class):
        """Test initialization fails when server is unreachable."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Connection refused")
        mock_session_class.return_value = mock_session

        with self.assertRaises(ConnectionError):
            Refine()

    @patch('refine_client.requests.Session')
    def test_init_verbose_mode(self, mock_session_class):
        """Test initialization with verbose mode."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine(verbose=True)
        self.assertTrue(refine.verbose)

    @patch('refine_client.requests.Session')
    def test_init_silent_mode(self, mock_session_class):
        """Test initialization with silent mode."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine(silent=True)
        self.assertTrue(refine.silent)


class TestRefineCSRFToken(unittest.TestCase):
    """Test cases for CSRF token handling."""

    @patch('refine_client.requests.Session')
    def setUp(self, mock_session_class):
        """Set up test fixtures."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        self.refine = Refine()
        self.mock_session = self.refine.session

    @patch('refine_client.requests.Session')
    def test_get_csrf_token_success(self, mock_session_class):
        """Test successful CSRF token retrieval."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        # Now set up the mock for _get_csrf_token
        token_response = Mock()
        token_response.json.return_value = {"token": "test_csrf_token_123"}
        refine.session.get.return_value = token_response

        token = refine._get_csrf_token()
        self.assertEqual(token, "test_csrf_token_123")
        self.assertEqual(refine.csrf_token, "test_csrf_token_123")

    @patch('refine_client.requests.Session')
    def test_get_csrf_token_cached(self, mock_session_class):
        """Test that CSRF token is cached after first retrieval."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        token_response = Mock()
        token_response.json.return_value = {"token": "cached_token"}
        refine.session.get.return_value = token_response

        token1 = refine._get_csrf_token()
        # Reset call count to check caching
        refine.session.get.reset_mock()
        token2 = refine._get_csrf_token()

        self.assertEqual(token1, token2)
        # Should not call again since it's cached
        self.assertEqual(refine.session.get.call_count, 0)

    @patch('refine_client.requests.Session')
    def test_get_csrf_token_missing(self, mock_session_class):
        """Test CSRF token retrieval fails when token is missing."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        token_response = Mock()
        token_response.json.return_value = {}
        refine.session.get.return_value = token_response

        with self.assertRaises(ValueError):
            refine._get_csrf_token()


class TestRefineIDResolution(unittest.TestCase):
    """Test cases for project ID resolution."""

    @patch('refine_client.requests.Session')
    def setUp(self, mock_session_class):
        """Set up test fixtures."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        self.refine = Refine()

    @patch('refine_client.requests.Session')
    def test_get_id_with_explicit_id(self, mock_session_class):
        """Test _get_id returns explicit project ID."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        result = refine._get_id("project_123")
        self.assertEqual(result, "project_123")

    @patch('refine_client.requests.Session')
    def test_get_id_with_loaded_id(self, mock_session_class):
        """Test _get_id returns loaded project ID."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "loaded_project"
        result = refine._get_id(None)
        self.assertEqual(result, "loaded_project")

    @patch('refine_client.requests.Session')
    def test_get_id_no_id_raises_error(self, mock_session_class):
        """Test _get_id raises error when no ID is available."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        with self.assertRaises(ValueError):
            refine._get_id(None)


class TestRefineProjectCreation(unittest.TestCase):
    """Test cases for project creation."""

    @patch('refine_client.requests.Session')
    def test_create_project_success(self, mock_session_class):
        """Test successful project creation."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.csrf_token = "test_token"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\nval1,val2\n")
            temp_file = f.name

        try:
            create_response = Mock()
            create_response.status_code = 200
            create_response.url = "http://127.0.0.1:3333/?project=1234567890"
            refine.session.post.return_value = create_response

            project_id = refine.create_project(temp_file, "Test Project")
            self.assertEqual(project_id, "1234567890")
            self.assertEqual(refine.project_id, "1234567890")
        finally:
            os.unlink(temp_file)

    @patch('refine_client.requests.Session')
    def test_create_project_file_not_found(self, mock_session_class):
        """Test project creation fails when file doesn't exist."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        with self.assertRaises(FileNotFoundError):
            refine.create_project("nonexistent.csv", "Test Project")

    @patch('refine_client.requests.Session')
    def test_create_project_upload_failed(self, mock_session_class):
        """Test project creation fails when upload returns error."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.csrf_token = "test_token"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\nval1,val2\n")
            temp_file = f.name

        try:
            error_response = Mock()
            error_response.status_code = 500
            error_response.text = "<html>Error</html>"
            refine.session.post.return_value = error_response

            with self.assertRaises(RuntimeError):
                refine.create_project(temp_file, "Test Project")
        finally:
            os.unlink(temp_file)
class TestRefineOperations(unittest.TestCase):
    """Test cases for applying operations."""

    @patch('refine_client.requests.Session')
    def test_apply_operation_success(self, mock_session_class):
        """Test successful operation application."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine(verbose=True)
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        operation = {
            "op": "core/column-removal",
            "columnName": "test_column",
            "description": "Remove test column"
        }

        op_response = Mock()
        op_response.status_code = 200
        op_response.json.return_value = {"code": "ok"}
        refine.session.post.return_value = op_response

        result = refine.apply_operation(operation)
        self.assertEqual(result, {"code": "ok"})

    @patch('refine_client.requests.Session')
    def test_apply_operation_failure(self, mock_session_class):
        """Test operation application fails on error status."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        operation = {"op": "core/column-removal", "columnName": "test_column"}

        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "<html>Error</html>"
        refine.session.post.return_value = error_response

        with self.assertRaises(RuntimeError):
            refine.apply_operation(operation)    @patch('refine_client.requests.Session')
    @patch('refine_client.requests.Session')
    def test_apply_multiple_operations(self, mock_session_class):
        """Test applying multiple operations."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        operations = [
            {"op": "core/column-removal", "columnName": "col1"},
            {"op": "core/column-removal", "columnName": "col2"}
        ]

        op_response = Mock()
        op_response.status_code = 200
        op_response.json.return_value = {"code": "ok"}
        refine.session.post.return_value = op_response

        results = refine.apply_operations(operations)
        self.assertEqual(len(results), 2)

    @patch('refine_client.requests.Session')
    def test_apply_operations_from_file(self, mock_session_class):
        """Test applying operations from a JSON file."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        operations = [
            {"op": "core/column-removal", "columnName": "col1"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(operations, f)
            temp_file = f.name

        try:
            op_response = Mock()
            op_response.status_code = 200
            op_response.json.return_value = {"code": "ok"}
            refine.session.post.return_value = op_response

            results = refine.apply_operations_from_file(temp_file)
            self.assertEqual(len(results), 1)
        finally:
            os.unlink(temp_file)

    @patch('refine_client.requests.Session')
    def test_apply_operations_from_file_not_found(self, mock_session_class):
        """Test apply_operations_from_file fails when file doesn't exist."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        with self.assertRaises(FileNotFoundError):
            refine.apply_operations_from_file("nonexistent.json")

    @patch('refine_client.requests.Session')
    @patch('refine_client.time.sleep')
    def test_apply_operation_with_wait(self, mock_sleep, mock_session_class):
        """Test applying operation with wait."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        operation = {"op": "core/column-removal", "columnName": "test_column"}

        op_response = Mock()
        op_response.status_code = 200
        op_response.json.return_value = {"code": "ok"}

        idle_response = Mock()
        idle_response.json.return_value = {"processes": []}

        refine.session.post.return_value = op_response
        refine.session.get.return_value = idle_response

        result = refine.apply_operation(operation, wait=True)
        self.assertEqual(result, {"code": "ok"})


class TestRefineExport(unittest.TestCase):
    """Test cases for data export."""

    @patch('refine_client.requests.Session')
    def test_export_data_success(self, mock_session_class):
        """Test successful data export."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "export.tsv")

            export_response = Mock()
            export_response.status_code = 200
            export_response.content = b"col1\tcol2\nval1\tval2\n"
            refine.session.post.return_value = export_response

            refine.export_data(output_file, "tsv")
            self.assertTrue(os.path.exists(output_file))

    @patch('refine_client.requests.Session')
    def test_export_data_failure(self, mock_session_class):
        """Test export data fails on error status."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "<html>Error</html>"
        refine.session.post.return_value = error_response

        with self.assertRaises(RuntimeError):
            refine.export_data("output.tsv", "tsv")


class TestRefineModelsAndColumns(unittest.TestCase):
    """Test cases for getting models and column information."""

    @patch('refine_client.requests.Session')
    def test_get_models_success(self, mock_session_class):
        """Test successful retrieval of models."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        mock_data = {
            "columnModel": {
                "columns": [
                    {"name": "col1"},
                    {"name": "col2"}
                ]
            }
        }

        models_response = Mock()
        models_response.status_code = 200
        models_response.json.return_value = mock_data
        refine.session.get.return_value = models_response

        result = refine.get_models()
        self.assertEqual(result, mock_data)

    @patch('refine_client.requests.Session')
    def test_get_column_names_success(self, mock_session_class):
        """Test successful retrieval of column names."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        mock_data = {
            "columnModel": {
                "columns": [
                    {"name": "col1"},
                    {"name": "col2"},
                    {"name": "col3"}
                ]
            }
        }

        names_response = Mock()
        names_response.status_code = 200
        names_response.json.return_value = mock_data
        refine.session.get.return_value = names_response

        result = refine.get_column_names()
        self.assertEqual(result, ["col1", "col2", "col3"])


class TestRefineProjectDeletion(unittest.TestCase):
    """Test cases for project deletion."""

    @patch('refine_client.requests.Session')
    def test_delete_project_success(self, mock_session_class):
        """Test successful project deletion."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        delete_response = Mock()
        delete_response.status_code = 200
        refine.session.post.return_value = delete_response

        refine.delete_project()
        refine.session.post.assert_called_once()

    @patch('refine_client.requests.Session')
    def test_delete_project_failure(self, mock_session_class):
        """Test project deletion fails on error status."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        error_response = Mock()
        error_response.status_code = 500
        error_response.text = "<html>Error</html>"
        refine.session.post.return_value = error_response

        with self.assertRaises(RuntimeError):
            refine.delete_project()


class TestRefineProjectMetadata(unittest.TestCase):
    """Test cases for project metadata operations."""

    @patch('refine_client.requests.Session')
    def test_get_all_projects_metadata_success(self, mock_session_class):
        """Test successful retrieval of all projects metadata."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        mock_data = {
            "projects": {
                "1234": {"name": "Project 1", "modified": "2025-01-01"},
                "5678": {"name": "Project 2", "modified": "2025-01-02"}
            }
        }

        metadata_response = Mock()
        metadata_response.status_code = 200
        metadata_response.json.return_value = mock_data
        refine.session.get.return_value = metadata_response

        result = refine.get_all_projects_metadata()
        self.assertEqual(len(result), 2)
        self.assertIn("1234", result)

    @patch('refine_client.requests.Session')
    def test_get_project_id_by_name_found(self, mock_session_class):
        """Test finding project ID by name."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        mock_data = {
            "projects": {
                "1234": {"name": "Test Project", "modified": "2025-01-01"},
                "5678": {"name": "Other Project", "modified": "2025-01-02"}
            }
        }

        metadata_response = Mock()
        metadata_response.status_code = 200
        metadata_response.json.return_value = mock_data
        # This get call is used for the initial connection in __init__ and for get_project_id_by_name
        refine.session.get.return_value = metadata_response

        result = refine.get_project_id_by_name("Test Project")
        self.assertEqual(result, "1234")

    @patch('refine_client.requests.Session')
    def test_set_project_metadata_success(self, mock_session_class):
        """Test successful project metadata update."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()
        refine.project_id = "test_project"
        refine.csrf_token = "test_token"

        meta_response = Mock()
        meta_response.status_code = 200
        refine.session.post.return_value = meta_response

        refine.set_project_metadata("name", "New Name")
        refine.session.post.assert_called_once()


class TestRefineRowsAsList(unittest.TestCase):
    """Test cases for rows_as_list utility method."""

    @patch('refine_client.requests.Session')
    def test_rows_as_list_with_data(self, mock_session_class):
        """Test rows_as_list converts row data correctly."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        data = {
            "rows": [
                {"cells": [{"v": "val1"}, {"v": "val2"}]},
                {"cells": [{"v": "val3"}, {"v": "val4"}]}
            ]
        }

        result = refine.rows_as_list(data)
        self.assertEqual(result, [["val1", "val2"], ["val3", "val4"]])

    @patch('refine_client.requests.Session')
    def test_rows_as_list_with_none_values(self, mock_session_class):
        """Test rows_as_list handles None values correctly."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        data = {
            "rows": [
                {"cells": [{"v": "val1"}, {}]},
                {"cells": [{}, {"v": "val2"}]}
            ]
        }

        result = refine.rows_as_list(data)
        self.assertEqual(result, [["val1", None], [None, "val2"]])

    @patch('refine_client.requests.Session')
    def test_rows_as_list_empty_rows(self, mock_session_class):
        """Test rows_as_list handles empty rows list."""
        mock_session = Mock()
        init_response = Mock()
        init_response.status_code = 200
        mock_session.get.return_value = init_response
        mock_session_class.return_value = mock_session

        refine = Refine()

        data = {"rows": []}
        result = refine.rows_as_list(data)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()

