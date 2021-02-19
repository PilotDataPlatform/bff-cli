import os
import zipfile
import time
import json
import enum
from ..config import ConfigClass
from ..commons.data_providers.redis import SrvRedisSingleton
import requests
from ..models.base_models import APIResponse, EAPIResponseCode
from ..commons.data_providers.models import Base, DataManifestModel, DataAttributeModel
from ..commons.data_providers.database import SessionLocal, engine

# Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_manifest_from_project(project_code, db_session):
    manifests = db_session.query(DataManifestModel.name, DataManifestModel.id).filter_by(project_code=project_code).all()
    manifest_in_project = []
    for m in manifests:
        manifest = {'name': m[0], 'id': m[1]}
        manifest_in_project.append(manifest)
    return manifest_in_project


def get_attributes_in_manifest(manifest, db_session):
    attr_list = []
    attributes = db_session.query(DataAttributeModel.name,
                                  DataAttributeModel.type,
                                  DataAttributeModel.optional,
                                  DataAttributeModel.value). \
        filter_by(manifest_id=manifest.get('id')). \
        order_by(DataAttributeModel.id.asc()).all()
    for attr in attributes:
        result = {"name": attr[0],
                  "type": attr[1],
                  "optional": attr[2],
                  "value": attr[3]}
        attr_list.append(result)
    return attr_list


def get_user_role(username):
    api_response = APIResponse()
    url = ConfigClass.NEO4J_SERVICE + "nodes/User/query"
    res = requests.post(
        url=url,
        json={"name": username}
    )
    users = json.loads(res.text)
    if len(users) == 0:
        api_response.error_msg = "token expired"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
    user_role = users[0]['role']
    return user_role


def query__node_has_relation_with_admin():
    url = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/query"
    data = {'is_all': 'true'}
    res = requests.post(url=url, json=data)
    project = res.json()
    return project


def query_node_has_relation_for_user(username):
    url = ConfigClass.NEO4J_SERVICE + "relations/query"
    data = {'start_params': {'name': username}}
    res = requests.post(url=url, json=data)
    res = res.json()
    project = []
    for i in res:
        project.append(i['end_node'])
    return project
