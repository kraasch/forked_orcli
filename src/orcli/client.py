# -*- coding: utf-8 -*-
# client.py
# (c) 2025 RK, Lic. CC-0

import json, time, requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class Refine:
    """Client interface for interacting with an OpenRefine server through its REST API."""
    DEFAULT_BASE_URL = "http://127.0.0.1:3333"
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url: str = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.session = requests.Session()
        self.csrf_token: str = ""
        self.project_id: str | None = None
        try:
            response = self.session.get(f"{self.base_url}")
            response.raise_for_status()
            logger.info(f"Connected to OpenRefine server at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenRefine server at {self.base_url}: {e}")
            raise ConnectionError(f"Could not connect to OpenRefine server at {self.base_url}") from e

    def _get_csrf_token(self) -> str:
        """Fetch CSRF token from server and cache it."""
        if not self.csrf_token:
            response = self.session.get(f"{self.base_url}/command/core/get-csrf-token")
            response.raise_for_status()
            token = response.json().get("token")
            if not token:
                logger.error("Failed to acquire CSRF token.")
                raise ValueError("CSRF token retrieval failed.")
            self.csrf_token = token
            logger.debug("CSRF token retrieved successfully.")
        return self.csrf_token

    def _get_id(self, project_id: str | None) -> str:
        """Resolve a project ID or use the currently loaded one."""
        if project_id:
            return project_id
        if not self.project_id:
            raise ValueError("No project ID specified or loaded.")
        return self.project_id

    def create_project(self, project_file: str, project_name: str) -> str:
        """Create a new project from a local file."""
        self._get_csrf_token()
        file_path = Path(project_file)
        if not file_path.is_file():
            logger.error(f"File not found: {project_file}")
            raise FileNotFoundError(project_file)

        logger.info(f"Creating OpenRefine project: {project_name}")
        with open(file_path, "rb") as f:
            files = {"project-file": (file_path.name, f)}
            params = {"project-name": project_name, "csrf_token": self.csrf_token}
            response = self.session.post(
                f"{self.base_url}/command/core/create-project-from-upload",
                params=params,
                files=files,
            )

        if response.status_code != 200:
            self._save_error_response(response, "Project creation failed.")
            raise RuntimeError(f"Failed to create project: {response.status_code}")

        parsed_url = urlparse(response.url)
        self.project_id = parse_qs(parsed_url.query).get("project", [None])[0]
        if not self.project_id:
            logger.error("Failed to parse project ID from server response.")
            raise ValueError("Project ID not found in response.")
        logger.info(f"Project created successfully: {self.project_id}")
        return self.project_id

    def apply_operations_from_file(self, operations_file: str, project_id: str | None = None, wait: bool = False):
        """Apply JSON operations from a given file."""
        file_path = Path(operations_file)
        if not file_path.is_file():
            raise FileNotFoundError(operations_file)
        with open(file_path, "r", encoding="utf-8") as f:
            operations = json.load(f)
        return self.apply_operations(operations, project_id, wait)

    def apply_operations(self, operations: list, project_id: str | None = None, wait: bool = False):
        """Apply a list of OpenRefine operations."""
        results = []
        for op in operations:
            results.append(self.apply_operation(op, project_id, wait))
        return results

    def apply_operation(self, operation: dict, project_id: str | None = None, wait: bool = False):
        """Apply a single operation to a project."""
        project = self._get_id(project_id)
        self._get_csrf_token()
        payload = {"operations": json.dumps([operation]), "csrf_token": self.csrf_token}
        response = self.session.post(
            f"{self.base_url}/command/core/apply-operations",
            params={"project": project},
            data=payload,
        )
        if response.status_code == 200:
            desc = operation.get("description", "Unnamed operation")
            logger.info(f"Applied operation: {desc}")
        else:
            self._save_error_response(response, "Operation failed.")
            raise RuntimeError(f"Operation failed: {response.status_code}")
        if wait:
            self.wait_until_idle(project)
        return response.json()

    def export_data(self, output_file: str = "exported_data.tsv", fmt: str = "tsv", project_id: str | None = None):
        """Export project data to file in specified format."""
        project = self._get_id(project_id)
        self._get_csrf_token()
        params = {"project": project, "format": fmt, "csrf_token": self.csrf_token}
        response = self.session.post(f"{self.base_url}/command/core/export-rows", params=params)
        if response.status_code != 200:
            self._save_error_response(response, "Export failed.")
            raise RuntimeError(f"Export failed: {response.status_code}")

        with open(output_file, "wb") as f:
            f.write(response.content)
        logger.info(f"Exported data to {output_file}")

    def get_models(self,project_id: str|None = None):
        """Get project models."""
        project = self._get_id(project_id)
        self._get_csrf_token()

        response = self.session.get(f'{self.base_url}/command/core/get-models',
                                     params={'project': project, 'csrf_token': self.csrf_token})
        if response.status_code == 200:
            logger.info(f"Get models {project}")
            data = response.json()
            return data
        else:
            self._save_error_response(response, 'Get models failed.')
            raise Exception(f'Get models failed: {response.status_code}')

    def get_column_names(self,project_id: str|None = None):
        """Get column names from project models."""
        project = self._get_id(project_id)
        self._get_csrf_token()

        response = self.session.get(f'{self.base_url}/command/core/get-models',
                                     params={'project': project, 'csrf_token': self.csrf_token})
        if response.status_code == 200:
            logger.info(f"Get column names {project}")
            data = response.json()["columnModel"]
            data = [col["name"] for col in data["columns"]]
            return data
        else:
            self._save_error_response(response, 'Get column names failed.')
            raise Exception(f'Get column names failed: {response.status_code}')

    def delete_project(self, project_id: str | None = None):
        """Delete a specific project."""
        project = self._get_id(project_id)
        self._get_csrf_token()
        response = self.session.post(
            f"{self.base_url}/command/core/delete-project",
            data={"project": project, "csrf_token": self.csrf_token},
        )
        if response.status_code == 200:
            logger.info(f"Deleted project {project}")
        else:
            self._save_error_response(response, "Project deletion failed.")
            raise RuntimeError(f"Deletion failed: {response.status_code}")

    def _save_error_response(self, response, message: str):
        """Save HTML error responses for debugging."""
        filename = "response.html"
        logger.error(f"{message}. Status: {response.status_code}")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.debug(f"Saved error details to {filename}")

    def get_all_projects_metadata(self) -> dict:
        """Retrieve metadata for all OpenRefine projects."""
        response = self.session.get(f"{self.base_url}/command/core/get-all-project-metadata")
        if response.status_code != 200:
            self._save_error_response(response, "Metadata retrieval failed.")
            raise RuntimeError("Failed to retrieve metadata.")
        logger.info("Retrieved all project metadata.")
        return response.json().get("projects", {})

    def get_project_id_by_name(self, name: str = "") -> str | None :
        """Get project id by project name"""
        projects = self.get_all_projects_metadata()
        for pid, metadata in projects.items():
            if metadata["name"] == name:
                logger.info("Retrieved project id.")
                return pid
        return None

    def set_project_metadata(self, field_name: str, value: str, id: str | None = None) -> None:
        project = self._get_id(id)
        self._get_csrf_token()
        data = {
            'project': project,
            'name': field_name,
            'value': value,
            'csrf_token': self.csrf_token
        }
        response = self.session.post(f'{self.base_url}/command/core/set-project-metadata', data=data)
        if response.status_code == 200:
            logger.info(f"Project metadata '{field_name}' updated to '{value}'.")
        else:
            self._save_error_response(response, "Failed to update project metadata")
            raise Exception(f"Failed to update project metadata: {response.status_code}")

    def wait_until_idle(self, project_id: str | None = None, delay: float = 0.5):
        """Wait until OpenRefine finishes processing all jobs."""
        project = self._get_id(project_id)
        while True:
            response = self.session.get(f"{self.base_url}/command/core/get-processes", params={"project": project})
            processes = response.json().get("processes", [])
            if processes:
                time.sleep(delay)
            else:
                logger.debug("OpenRefine is idle.")
                break

    def rows_as_list(self, data:dict)->list:
        """Return rows as list"""
        if 'rows' in data:
            rows_list = [
                [cell.get("v", None) for cell in row["cells"]]
                for row in data["rows"]
            ]
            return rows_list
        else:
            return []

if __name__ == "__main__":
    refine = Refine()

