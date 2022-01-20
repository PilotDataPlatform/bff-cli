from pydantic import BaseModel, Field
from .base_models import APIResponse


class CheckFileResponse(APIResponse):
    result: dict = Field({}, example={
        "id": 2077,
        "labels": [
            "File",
            "Greenroom"
            "Raw"
        ],
        "global_entity_id": "file_data-2a7ea1d8-7dea-11eb-8428-be498ca98c54-1614973025",
        "operator": "",
        "file_size": 1048576,
        "tags": [],
        "archived": "false",
        "path": "/data/vre-storage/mar04/raw",
        "time_lastmodified": "2021-03-05T19:37:06",
        "uploader": "admin",
        "process_pipeline": "",
        "name": "Testdateiäöüßs4",
        "time_created": "2021-03-05T19:37:06",
        "guid": "f91b258d-2f1d-409a-9551-91af8057e70e",
        "full_path": "/data/vre-storage/mar04/raw/Testdateiäöüßs4",
        "generate_id": "undefined"
    }
    )
