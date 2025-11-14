import json 
import logging
from refine_client import Refine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

refine = Refine()
if False:
    pid = refine.get_project_id_by_name("Noch hochzuladen")
    print(pid)
    refine.project_id = pid
    print(refine.get_column_names())
    op = [{
        "op": "core/column-addition",
        "engineConfig": {
        "facets": [],
        "mode": "row-based"
        },
        "baseColumnName": "ImageDescription",
        "expression": "jython:return \"== {{int:filedesc}} ==\\n{{Information}}\\n{{Location|\" + cells['GPSPosition'].value.replace(',','|') + \"}}\\n\\n== {{int:license-header}} ==\\n{{User:Reinhard Kraasch/licence}}\\n\\n[[Category:\" + cells['Category'].value + \"]]\\n[[Category:Files by Reinhard Kraasch]]\"",
        "onError": "set-to-blank",
        "newColumnName": "Wikitext1",
        "columnInsertIndex": 4,
        "description": "Spalte 'Wikitext1' anlegen"
    }]        
            
    print(json.dumps(op, indent=2, ensure_ascii=False))
    print(refine.apply_operations(op))
    print(refine.get_column_names())
else:
    projects = refine.get_all_projects_metadata()
    for pid, metadata in projects.items():
        if metadata["name"] not in ["TestProjekt","MeinProjekt"]:
            logger.info(f"Existing Project {pid}: {metadata['name']}")
        else:
            logger.info(f"Delete Project {pid}: {metadata['name']}")
            refine.delete_project(pid)
    pid = refine.create_project("Test\\metadata.csv", "MeinProjekt")
    refine.set_project_metadata("description", "Dies ist ein Testprojekt.")
    refine.set_project_metadata("name", "TestProjekt")
    refine.export_data("Test\\data.tsv", "tsv")
    logger.info("Columns: " + str(refine.get_column_names()))
    logger.info("Models: " + json.dumps(refine.get_models(),indent=2))