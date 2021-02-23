import json
import requests
from ..config import ConfigClass
from ..resources. error_handler import customized_error_template, ECustomizedError
from ..models.base_models import APIResponse, EAPIResponseCode
from ..commons.data_providers.data_models import DataManifestModel, DataAttributeModel
from ..commons.data_providers.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_manifest_name_from_project_in_db(event):
    project_code = event.get('project_code')
    manifest_name = event.get('manifest_name', None)
    db_session = event.get('session')
    if manifest_name:
        m = db_session.query(DataManifestModel.name,
                             DataManifestModel.id)\
            .filter_by(project_code=project_code, name=manifest_name)\
            .first()
        if not m:
            return None
        else:
            manifest = {'name': m[0], 'id': m[1]}
            return manifest
    else:
        manifests = db_session.query(DataManifestModel.name,
                                     DataManifestModel.id)\
            .filter_by(project_code=project_code)\
            .all()
        manifest_in_project = []
        for m in manifests:
            manifest = {'name': m[0], 'id': m[1]}
            manifest_in_project.append(manifest)
        return manifest_in_project


def get_attributes_in_manifest_in_db(event):
    manifest = event.get('manifest')
    db_session = event.get('session')
    attr_list = []
    attributes = db_session.query(DataAttributeModel.name,
                                  DataAttributeModel.type,
                                  DataAttributeModel.optional,
                                  DataAttributeModel.value). \
        filter_by(manifest_id=manifest.get('id')). \
        order_by(DataAttributeModel.id.asc()).all()
    if not attributes:
        return None
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
    try:
        res = requests.post(
            url=url,
            json={"name": username}
        )
        users = json.loads(res.text)
        if len(users) == 0:
            api_response.error_msg = customized_error_template(ECustomizedError.TOKEN_EXPIRED)
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        user_role = users[0]['role']
        return user_role
    except Exception:
        return None


def query__node_has_relation_with_admin():
    url = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/query"
    data = {'is_all': 'true'}
    try:
        res = requests.post(url=url, json=data)
        project = res.json()
        return project
    except Exception:
        return None


def query_node_has_relation_for_user(username):
    url = ConfigClass.NEO4J_SERVICE + "relations/query"
    data = {'start_params': {'name': username}}
    try:
        res = requests.post(url=url, json=data)
        res = res.json()
        project = []
        for i in res:
            project.append(i['end_node'])
        return project
    except Exception:
        return None


def query_file_in_project(dataset_id, filename):
    url = ConfigClass.FILEINFO_HOST + "v1/files/%s/query" % str(dataset_id)
    if filename:
        data = {"query": {
            "name": filename,
            "labels": ["File"]}}
    else:
        data = {"query": {"labels": ["File"]}}
    try:
        res = requests.post(url=url, json=data)
        res = res.json()
        return res
    except Exception:
        return None


def get_file_path(project_code, file_name):
    post_data = {"code": project_code}
    response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/Dataset/query", json=post_data)
    if not response.json():
        return None
    project_info = response.json()[0]
    project_id = project_info.get('id')
    res = query_file_in_project(project_id, file_name)
    file_path = res.get('result')[0].get('path')
    return file_path


def get_file_node(full_path):
    post_data = {"full_path": full_path}
    try:
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/File/query", json=post_data)
        if not response.json():
            return None
        return response.json()[0]
    except Exception:
        return None


def attach_manifest_to_file(file_path, manifest_id, attributes):
    file_node = get_file_node(file_path)
    if not file_node:
        return None
    file_id = file_node["id"]
    post_data = {"manifest_id": manifest_id}
    if attributes:
        for key, value in attributes.items():
            post_data["attr_" + key] = value
    response = requests.put(ConfigClass.NEO4J_SERVICE + f"nodes/File/node/{file_id}", json=post_data)
    if not response.json():
        return None
    return response.json()


def validate_has_non_optional_attribute_field(input_attributes, compare_attr):
    if not compare_attr.get('optional') and not compare_attr.get('name') in input_attributes:
        return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES)


def validate_attribute_field_by_value(input_attributes, compare_attr):
    attr_name = compare_attr.get('name')
    value = input_attributes.get(attr_name)
    if value and compare_attr.get('type') == "text":
        if len(value) > 100:
            return customized_error_template(ECustomizedError.TEXT_TOO_LONG) % attr_name
    elif value and compare_attr.get('type') == 'multiple_choice':
        if value not in compare_attr.get('value').split(","):
            return customized_error_template(ECustomizedError.INVALID_CHOICE) % attr_name
    else:
        if not compare_attr.get('optional'):
            return customized_error_template(ECustomizedError.FIELD_REQUIRED) % attr_name


def validate_attribute_name(input_attributes, exist_attributes):
    valid_attributes = [attr.get('name') for attr in exist_attributes]
    for key, value in input_attributes.items():
        if key not in valid_attributes:
            return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % key


def has_valid_attributes(event):
    attributes = event.get('attributes')
    exist_attributes = get_attributes_in_manifest_in_db(event)
    _name_error = validate_attribute_name(attributes, exist_attributes)
    if _name_error:
        return _name_error
    for attr in exist_attributes:
        required_attr = attr.get('name')
        if not attr.get('optional') and required_attr not in attributes:
            return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES) % required_attr
        elif attr not in exist_attributes:
            return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % attr
        else:
            _optional_error = validate_has_non_optional_attribute_field(attributes, attr)
            if _optional_error:
                return _optional_error
            _value_error = validate_attribute_field_by_value(attributes, attr)
            if _value_error:
                return _value_error
