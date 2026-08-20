
import pytest

from refine_client import Refine

def test_create_project():
    # Create a small CSV file for the new OpenRefine project.
    csv_file = "test_data.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("name,age\nAlice,30\nBob,25\n")
    refine = Refine()
    try:
        project_id = refine.create_project(
            project_file=csv_file,
            project_name="pytest-test-project",
        )
        # Verify that OpenRefine created a project.
        assert project_id is not None
        assert refine.project_id == project_id
        # Verify the table/columns were created correctly.
        columns = refine.get_column_names(project_id)
        assert columns == ["name", "age"]
    finally:
        pass
        # Clean up the test project.
        if refine.project_id:
            refine.delete_project(refine.project_id)

# def test_manipulate_data():
#     import json
#     import os
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
#     refine = Refine()
#     # pid = refine.get_project_id_by_name("Noch hochzuladen")
#     # print(pid)
#     # refine.project_id = pid
#     # print(refine.get_column_names())
#     # op = [{
#     #     "op": "core/column-addition",
#     #     "engineConfig": {
#     #     "facets": [],
#     #     "mode": "row-based"
#     #     },
#     #     "baseColumnName": "ImageDescription",
#     #     "expression": "jython:return \"== {{int:filedesc}} ==\\n{{Information}}\\n{{Location|\" + cells['GPSPosition'].value.replace(',','|') + \"}}\\n\\n== {{int:license-header}} ==\\n{{User:Reinhard Kraasch/licence}}\\n\\n[[Category:\" + cells['Category'].value + \"]]\\n[[Category:Files by Reinhard Kraasch]]\"",
#     #     "onError": "set-to-blank",
#     #     "newColumnName": "Wikitext1",
#     #     "columnInsertIndex": 4,
#     #     "description": "Spalte 'Wikitext1' anlegen"
#     # }]
#     # print(json.dumps(op, indent=2, ensure_ascii=False))
#     # print(refine.apply_operations(op))
#     # print(refine.get_column_names())
#     projects = refine.get_all_projects_metadata()
#     for pid, metadata in projects.items():
#         if metadata["name"] not in ["TestProjekt","MeinProjekt"]:
#             logger.info(f"Existing Project {pid}: {metadata['name']}")
#         else:
#             logger.info(f"Delete Project {pid}: {metadata['name']}")
#             refine.delete_project(pid)
#     pid = refine.create_project(os.path.join("data", "metadata.csv"), "MeinProjekt")
#     refine.set_project_metadata("description", "Dies ist ein Testprojekt.")
#     refine.set_project_metadata("name", "TestProjekt")
#     refine.export_data(os.path.join("data", "metadata.tsv"), "tsv")
#     logger.info("Columns: " + str(refine.get_column_names()))
#     logger.info("Models: " + json.dumps(refine.get_models(),indent=2))
# 
