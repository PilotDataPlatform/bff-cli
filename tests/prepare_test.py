from app.config import ConfigClass
import httpx
from app.main import create_app
import time

class SetupTest:

    def __init__(self, log):
        self.log = log
        self.client = create_app()

    def auth(self, payload=None):
        if not payload:
            payload = {
                "username": "jzhang10",
                "password": "CMDvrecli2021!"
            }
        url = ConfigClass.AUTH_SERVICE + "/v1/users/auth"
        self.log.info(url)
        with httpx.Client() as client:
            response = client.post(url, json=payload)
        data = response.json()
        self.log.info(data)
        return data["result"].get("access_token")

    def login_collaborator(self):
        return {"username": "jzhang3", "password": "Indoc1234567!"}

    def login_contributor(self):
        return {"username": "jzhang33", "password": "Indoc1234567!"}

    def get_user(self):
        payload = {
            "name": "jzhang10",
        }
        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/User/query", json=payload)
        self.log.info(response.json())
        return response.json()[0]

    def create_project(self, code, discoverable='true'):
        self.log.info("\n")
        self.log.info("Preparing testing project".ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/Container"
        params = {"name": "BFFCLIUnitTest",
                  "path": code,
                  "code": code,
                  "description": "Project created by unit test, will be deleted soon...",
                  "discoverable": discoverable,
                  "type": "Usecase",
                  "tags": ['test']
                  }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {params}")
        try:
            with httpx.Client() as client:
                res = client.post(testing_api, json=params)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            return res.json() [0]
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e

    def delete_project(self, node_id):
        self.log.info("\n")
        self.log.info("Preparing delete project".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/Container/node/%s" % str(node_id)
        try:
            with httpx.Client() as client:
                delete_res = client.delete(delete_api)
            self.log.info(f"DELETE STATUS: {delete_res.status_code}")
            self.log.info(f"DELETE RESPONSE: {delete_res.text}")
        except Exception as e:
            self.log.info(f"ERROR DELETING PROJECT: {e}")
            self.log.info(f"PLEASE DELETE THE PROJECT MANUALLY WITH ID: {node_id}")
            raise e

    def add_user_to_project(self, user_id, project_id, role):
        payload = {
            "start_id": user_id,
            "end_id": project_id,
        }
        with httpx.Client() as client:
            response = client.post(ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations/{role}", json=payload)
        if response.status_code != 200:
            raise Exception(f"Error adding user to project: {response.json()}")

    def remove_user_from_project(self, user_id, project_id):
        payload = {
            "start_id": user_id,
            "end_id": project_id,
        }
        with httpx.Client() as client:
            response = client.delete(ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations", params=payload)
        self.log.info(f'User removed from project: {response.text}')
        if response.status_code != 200:
            raise Exception(f"Error removing user from project: {response.json()}")

    def get_projects(self):
        all_project_url = ConfigClass.NEO4J_SERVICE + '/v1/neo4j/nodes/Container/properties'
        try:
            with httpx.Client() as client:
                response = client.get(all_project_url)
            if response.status_code == 200:
                res = response.json()
                projects = res.get('code')
                self.log.info(f'Get projects total number: {len(projects)}')
                return projects
            else:
                self.log.error(f"RESPONSE ERROR: {response.text}")
                return None
        except Exception as e:
            raise e

    def generate_entity_id(self):
        self.log.info("Generating global entity ID".ljust(80, '-'))
        testing_api = ConfigClass.UTILITY_SERVICE + "/v1/utility/id"
        self.log.info(f"Request API: {testing_api}")
        with httpx.Client() as client:
            res = client.get(testing_api)
        self.log.info(f"Request response: {res.text}")
        if not res.json():
            return None
        else:
            return res.json()['result']

    def get_folder(self, folder, project_code, zone):
        self.log.info("get_folder".ljust(80, '-'))
        try:
            url = ConfigClass.NEO4J_SERVICE + "/v2/neo4j/nodes/query"
            layers = folder.split('/')
            self.log.info(f"Folder layers: {layers}")
            if len(layers) == 1:
                folder_name = layers[0]
            else:
                folder_name = layers[-1]
            payload = {
                "query": {
                    "name": folder_name,
                    "project_code": project_code,
                    "display_path": folder,
                    "labels": [
                        "Folder",
                        zone,
                    ]
                }
            }
            self.log.info(f"Request url: {url}")
            self.log.info(f"Getting folder payload: {payload}")
            with httpx.Client() as client:
                res = client.post(url, json=payload)
            self.log.info(f"Getting folder response: {res.text}")
            result = res.json().get("result")[0]
            self.log.info(f'Getting folder result: {result}')
            return result
        except Exception as e:
            raise Exception(f"Error getting folder: {e}")

    def create_file(self, project_code, filename,
                    folder=None, zone=ConfigClass.GREEN_ZONE_LABEL, uploader='jzhang'):
        self.log.info("\n")
        self.log.info("Preparing testing file".ljust(80, '-'))
        self.log.info(f"File will be created in {zone} under {folder}")
        testing_api = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/File"
        relation_api = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations/own"
        global_entity_id = self.generate_entity_id()
        if zone.lower() == ConfigClass.CORE_ZONE_LABEL.lower():
            root_path = "/vre-data"
            file_label = ConfigClass.CORE_ZONE_LABEL
        else:
            root_path = "/data/vre-storage"
            file_label = ConfigClass.GREEN_ZONE_LABEL
        if folder:
            payload = {
                "name": filename,
                "global_entity_id": global_entity_id,
                "extra_labels": [file_label],
                "file_size": 7120,
                "operator": uploader,
                "archived": False,
                "process_pipeline": "",
                "project_code": project_code,
                "uploader": uploader,
                "generate_id": "undefined",
                "display_path": f"{uploader}/{folder}/{filename}",
                "list_priority": 20,
                "location": f"unittest://fake-minio-location/{project_code}/{uploader}",
                "parent_folder_geid": "a451d123-9e1d-4648-b3a2-5f207560c8a1-1622475624",
                "full_path": f"{root_path}/{project_code}/{uploader}/{folder}/{filename}",
                "tags": []
            }
            folder_information = self.get_folder(f"{uploader}/{folder}", project_code, file_label)
            relation_payload = {'start_id': folder_information.get('id')}
        else:
            payload = {
                        "name": filename,
                        "global_entity_id": global_entity_id,
                        "extra_labels": [file_label],
                        "file_size": 7120,
                        "operator": uploader,
                        "archived": False,
                        "process_pipeline": "unittest",
                        "project_code": project_code,
                        "uploader": uploader,
                        "generate_id": "undefined",
                        "display_path": f"{uploader}/{filename}",
                        "list_priority": 20,
                        "location": f"unittest://fake-minio-location/gr-{project_code}/{uploader}/{filename}",
                        "parent_folder_geid": "c01ceeb2-9fd0-4c7c-8dba-c4e5a760a935-1625673658",
                        "full_path": f"{root_path}/{project_code}/{uploader}/{filename}",
                        "tags": []
            }
            folder_information = self.get_folder(uploader, project_code, file_label)
            relation_payload = {'start_id': folder_information.get('id')}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {payload}")
        try:
            with httpx.Client() as client:
                res = client.post(testing_api, json=payload)
                self.log.info(f"RESPONSE DATA: {res.text}")
                self.log.info(f"RESPONSE STATUS: {res.status_code}")
                assert res.status_code == 200
                res = res.json()[0]
                relation_payload['end_id'] = res.get('id')
                self.log.info(f"CREATING RELATION WITH start_id: {relation_payload.get('start_id')}")
                
                relation_res = client.post(relation_api, json=relation_payload)
            self.log.info(f"Relation response: {relation_res.text}")
            assert relation_res.status_code == 200
            es_record = self.create_es_record(payload)
            assert es_record.json().get('code') == 200
            return res
        except Exception as e:
            self.log.info(f"ERROR CREATING FILE: {e}")
            raise e

    def create_es_record(self, data):
        self.log.info(f"CREATING ES RECORD: {data}")
        try:
            url = ConfigClass.PROVENANCE_SERVICE + '/v1/entity/file'
            path = data.get('full_path')
            root_path = path.strip('/').split('/')[0]
            self.log.info(f"File root path: {root_path}")
            if root_path == 'data':
                zone = ConfigClass.CORE_ZONE_LABEL.lower()
            else:
                zone = ConfigClass.GREEN_ZONE_LABEL.lower()
            time_stamp = int(time.time()*1000)
            payload = data.copy()
            payload['zone'] = zone
            payload['time_created'] = time_stamp
            payload['time_lastmodified'] = time_stamp
            payload['atlas_guid'] = 'unittest file'
            payload['data_type'] = 'File'
            payload['file_type'] = 'raw'
            payload['file_name'] = payload.get('name')
            self.log.info(f"ES URL: {url}")
            self.log.info(f"ES PAYLOAD: {payload}")
            with httpx.Client() as client:
                res = client.post(url, json=payload)
            self.log.info(f"ES RESPONSE: {res.text}")
            return res
        except Exception as e:
            raise e

    def delete_file(self, node_id):
        self.log.info("\n")
        self.log.info("Delete testing file".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/File/node/%s" % node_id
        payload = {
                    "id": node_id,
                    "label": "File"
        }
        self.log.info(f"POST API: {delete_api}")
        self.log.info(f"POST params: {payload}")
        try:
            with httpx.Client() as client:
                res = client.delete(delete_api, params=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            return res.json()[0]
        except Exception as e:
            self.log.info(f"ERROR DELETE FILE: {e}")
            raise e
