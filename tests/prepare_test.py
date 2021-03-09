from app.config import ConfigClass
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import create_app

class SetupTest:
    def __init__(self, log):
        self.log = log

    def auth(self):
        payload = {
            "username": "jzhang10",
            "password": "CMDvrecli2021!",
            "realm": "vre"
        }
        response = requests.post(ConfigClass.AUTH_SERVICE + "/v1/users/auth", json=payload)
        data = response.json()
        print(data)
        return data["result"].get("access_token")

    def get_user(self):
        payload = {
            "name": "jzhang10",
        }
        response = requests.post(ConfigClass.NEO4J_SERVICE + "nodes/User/query", json=payload)
        print(response.json())
        return response.json()[0]

    def create_project(self, code, discoverable='true'):
        self.log.info("\n")
        self.log.info("Preparing testing project".ljust(80, '-'))
        testing_api = ConfigClass.NEO4J_SERVICE+ "nodes/Dataset"
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
        if response.status_code != 200:
            raise Exception(f"Error removing user from project: {response.json()}")
