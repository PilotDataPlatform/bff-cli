from app.config import ConfigClass
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import create_app
from app.resources.helpers import get_dataset_node


class SetupTest:
    def __init__(self, log):
        self.log = log
        app = create_app()
        self.client = TestClient(app)

    def auth(self, payload=None):
        if not payload:
            payload = {
                "username": "jzhang10",
                "password": "CMDvrecli2021!",
                "realm": "vre"
            }
        response = requests.post(ConfigClass.AUTH_SERVICE + "/v1/users/auth", json=payload)
        data = response.json()
        self.log.info(data)
        return data["result"].get("access_token")

    def get_user(self):
        payload = {
            "name": "jzhang10",
        }
        response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/User/query", json=payload)
        self.log.info(response.json())
        return response.json()[0]

    def create_project(self, code, discoverable='true'):
        self.log.info("\n")
        self.log.info("Preparing testing project".ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_SERVICE + "nodes/Dataset"
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
            res = requests.post(testing_api, json=params)
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
        delete_api = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/node/%s" % str(node_id)
        try:
            delete_res = requests.delete(delete_api)
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
        response = requests.post(ConfigClass.NEO4J_SERVICE + "relations/{role}", json=payload)
        if response.status_code != 200:
            raise Exception(f"Error adding user to project: {response.json()}")


    def remove_user_from_project(self, user_id, project_id):
        payload = {
            "start_id": user_id,
            "end_id": project_id,
        }
        response = requests.delete(ConfigClass.NEO4J_SERVICE + "relations", params=payload)
        self.log.info(f'User removed from project: {response.text}')
        if response.status_code != 200:
            raise Exception(f"Error removing user from project: {response.json()}")

    def get_projects(self):
        all_project_url = ConfigClass.NEO4J_SERVICE + 'nodes/Dataset/properties'
        try:
            response = requests.get(all_project_url)
            if response.status_code == 200:
                res = response.json()
                projects = res.get('code')
                return projects
            else:
                self.log.error(f"RESPONSE ERROR: {response.text}")
                return None
        except Exception as e:
            raise e

    def generate_entity_id(self):
        self.log.info("Generating global entity ID")
        testing_api = ConfigClass.COMMON_SERVICE
        res = requests.get(testing_api)
        if not res.json():
            return None
        else:
            return res.json()['result']

    def create_file(self, project_code, filename):
        self.log.info("\n")
        self.log.info("Preparing testing file".ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_SERVICE + "nodes/File"
        relation_api = ConfigClass.NEO4J_SERVICE + "relations/own"
        global_entity_id = self.generate_entity_id()
        payload = {
                    "name": filename,
                    "global_entity_id": global_entity_id,
                    "extra_labels": ["Greenroom"],
                    "file_size": 7120,
                    "operator": "jzhang",
                    "archived": False,
                    "process_pipeline": "",
                    "project_code": project_code,
                    "uploader": "jzhang",
                    "generate_id": "undefined",
                    "path": f"/data/vre-storage/{project_code}/raw",
                    "full_path": f"/data/vre-storage/{project_code}/raw/{filename}"
        }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {payload}")
        try:
            res = requests.post(testing_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            res = res.json()[0]
            project_info = get_dataset_node(project_code)
            self.log.info(f"Project info: {project_info}")
            project_id = project_info.get('id')
            relation_payload = {'start_id': project_id,
                                'end_id': res.get('id')}
            relation_res = requests.post(relation_api, json=relation_payload)
            self.log.info(f"Relation response: {relation_res.text}")
            assert relation_res.status_code == 200
            return res
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e

    def delete_file(self, node_id):
        self.log.info("\n")
        self.log.info("Delete testing file".ljust(80, '-'))
        delete_api = ConfigClass.NEO4J_SERVICE + "nodes/File/node/%s" % node_id
        payload = {
                    "id": node_id,
                    "label": "File"
        }
        self.log.info(f"POST API: {delete_api}")
        self.log.info(f"POST params: {payload}")
        try:
            res = requests.delete(delete_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            assert res.status_code == 200
            return res.json()[0]
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e
