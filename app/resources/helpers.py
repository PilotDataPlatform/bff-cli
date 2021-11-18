import json
import requests
import time
from ..config import ConfigClass
from ..resources. error_handler import customized_error_template, ECustomizedError
from ..models.base_models import APIResponse, EAPIResponseCode
from ..models.error_model import HPCError
from ..service_logger.logger_factory_service import SrvLoggerFactory

_logger = SrvLoggerFactory("Helpers").get_logger()


def get_zone(namespace):
    return {"greenroom": "Greenroom",
            "vrecore": "VRECore"}.get(namespace.lower(), 'greenroom')


def get_path_by_zone(namespace, project_code):
    return {"greenroom": f"/data/vre-storage/{project_code}/",
            "vrecore": f"/vre-data/{project_code}/"
            }.get(namespace.lower(), 'greenroom')
            

def get_user_role(user_id, project_id):
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations"
    try:
        res = requests.get(
            url=url,
            params={"start_id": user_id,
                    "end_id": project_id})
        _res = json.loads(res.text)[0]
        return _res
    except Exception:
        return None


def query__node_has_relation_with_admin(label='Container'):
    _logger.info("query__node_has_relation_with_admin".center(80, '-'))
    url = ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/{label}/query"
    _logger.info(f"Requesting API: {url}")
    data = {'is_all': 'true'}
    try:
        res = requests.post(url=url, json=data)
        project = res.json()
        return project
    except Exception:
        return []

def query_node_has_relation_for_user(username, label='Container'):
    _logger.info("query_node_has_relation_for_user".center(80, '-'))
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations/query"
    data = {
        'start_label': 'User',
        'start_params': {'name': username},
        'end_label': label
    }
    _logger.info(f"Requesting API: {url}")
    _logger.info(f'Query payload: {data}')
    try:
        res = requests.post(url=url, json=data)
        _logger.info(f'Query response: {res.text}')
        res = res.json()
        return res
    except Exception:
        return []
    
def get_node_by_geid(geid):
    _logger.info("get_node_by_geid".center(80, '-'))
    url = ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/geid/{geid}"
    _logger.info(f'Getting node: {url}')
    try:
        res = requests.get(url)
        _logger.info(f'Getting node info: {res.text}')
        result = res.json()
    except Exception as e:
        _logger.error(f'Error getting node by geid: {e}')
        result = None
    return result


def batch_query_node_by_geid(geid_list):
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/query/geids"
    payload = {
        "geids": geid_list
    }
    res = requests.post(url, json=payload)
    res_json = res.json()
    result = res_json.get('result')
    located_geid = []
    query_result = {}
    for node in result:
        geid = node.get('global_entity_id', '')
        if geid in geid_list:
            located_geid.append(geid)
            query_result[geid] = node
    return located_geid, query_result


def query_file_in_project(project_code, filename, zone='Greenroom'):
    _logger.info("query_file_in_project".center(80, '-'))
    url = ConfigClass.NEO4J_SERVICE + "/v2/neo4j/nodes/query"
    path = get_path_by_zone(zone, project_code) + filename
    data = {"query": {
        "name": filename.split('/')[-1],
        "full_path": path,
        "archived": False,
        "project_code": project_code,
        "labels": ["File", zone]}}
    _logger.info(f"Query url: {url}")
    try:
        _logger.info(f"Get file info payload: {data}")
        res = requests.post(url=url, json=data)
        _logger.info(f"Query file response: {res.text}")
        file_res = res.json()
        _logger.info(f"file response: {file_res}")
        if file_res.get('code') == 200 and file_res.get('result'):
            return file_res
        else:
            _logger.info("Get name as folder")
            _logger.info(filename.split('/'))
            if len(filename.split('/')) < 2:
                relative_path = ''
            else:
                relative_path = '/'.join(filename.split('/')[0: -1])
            _logger.info(f'relative_path: {relative_path}')
            folder = {"query": {
                "name": filename.split('/')[-1],
                "folder_relative_path": relative_path,
                "archived": False,
                "project_code": project_code,
                "labels": ["Folder", zone]}}
            _logger.info(f"Query folder payload: {folder}")
            _res = requests.post(url=url, json=folder)
            _logger.info(f"Query folder response: {_res.text}")
            _res = _res.json()
            if _res.get('code') == 200 and _res.get('result'):
                return _res
            else:
                return []
    except Exception as e:
        _logger.error(str(e))
        return []


def get_file_entity_id(project_code, file_name, zone='Greenroom'):
    res = query_file_in_project(project_code, file_name, zone)
    res = res.get('result')
    if not res:
        return None
    else:
        global_entity_id = res[0].get('global_entity_id')
        return global_entity_id


def get_file_by_id(file_id):
    post_data = {"global_entity_id": file_id}
    try:
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/File/query", json=post_data)
        if not response.json():
            return None
        return response.json()[0]
    except Exception:
        return None


def get_node_by_code(code, label):
    post_data = {"code": code}
    try:
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/{label}/query", json=post_data)
        if not response.json():
            return None
        return response.json()[0]
    except Exception:
        return None


def has_permission(event):
    _logger.info("has_permission".center(80, '-'))
    user_role = event.get('user_role')
    username = event.get('username')
    project_code = event.get('project_code')
    _logger.info(f"user role: {user_role}, user name: {username}, project code: {project_code}")
    if user_role == 'admin':
        result = 'permit'
        code = EAPIResponseCode.success
    else:
        _projects = get_user_projects(user_role, username)
        _projects = [p.get('code') for p in _projects]
        if project_code not in _projects:
            result = customized_error_template(ECustomizedError.PERMISSION_DENIED)
            code = EAPIResponseCode.forbidden
        else:
            result = 'permit'
            code = EAPIResponseCode.success
    return code, result


def get_user_projects(user_role, username):
    _logger.info("get_user_projects".center(80, '-'))
    _logger.info(f'Current username: {username}')
    projects_list = []
    if user_role == "admin":
        project_candidate = query__node_has_relation_with_admin()
    else:
        projects = query_node_has_relation_for_user(username)
        project_candidate = []
        for p in projects:
            _logger.info(f"Found project status: {p['r']}")
            if p['r'].get('status', 'hibernated') == 'active':
                project_candidate.append(p['end_node'])
            else:
                _logger.info(f"Disabled project: {p['end_node']}")
        _logger.info(f'Found projects: {project_candidate}')
    _logger.info(f"Number of candidates: {len(project_candidate)}")
    for p in project_candidate:
        res_projects = {'name': p.get('name'),
                        'code': p.get('code'),
                        'id': p.get('id'),
                        'geid': p.get('global_entity_id')}
        projects_list.append(res_projects)
    _logger.info(f"Number of projects found: {len(projects_list)}")
    return projects_list


def attach_manifest_to_file(event):
    project_code = event.get('project_code')
    global_entity_id = event.get('global_entity_id')
    manifest_id = event.get('manifest_id')
    attributes = event.get('attributes')
    username = event.get('username')
    project_role = event.get('project_role')
    _logger.info("attach_manifest_to_file".center(80, '-'))
    url = ConfigClass.FILEINFO_HOST + "/v1/files/attributes/attach"
    payload = {"project_code": project_code,
               "manifest_id": manifest_id,
               "global_entity_id": [global_entity_id],
               "attributes": attributes,
               "inherit": True,
               "project_role": project_role,
               "username": username}
    _logger.info(f"POSTING: {url}")
    _logger.info(f"PAYLOAD: {payload}")
    response = requests.post(url=url, json=payload)
    _logger.info(f"RESPONSE: {response.text}")
    if not response.json():
        return None
    return response.json()


def http_query_node_zone(folder_event):
    namespace = folder_event.get('namespace')
    project_code = folder_event.get('project_code')
    folder_name = folder_event.get('folder_name')
    display_path = folder_event.get('display_path')
    folder_relative_path = folder_event.get('folder_relative_path')
    zone_label = get_zone(namespace)
    payload = {
        "query": {
            "folder_relative_path": folder_relative_path,
            "display_path": display_path,
            "name": folder_name,
            "project_code": project_code,
            "labels": ['Folder', zone_label]}
    }
    node_query_url = ConfigClass.NEO4J_SERVICE + "/v2/neo4j/nodes/query"
    response = requests.post(node_query_url, json=payload)
    return response


def get_parent_label(source):
    return {
        'folder': 'Folder',
        'container': 'Container'
    }.get(source.lower(), None)


def separate_rel_path(folder_path):
    folder_layers = folder_path.strip('/').split('/')
    if len(folder_layers) > 1:
        rel_path = '/'.join(folder_layers[:-1])
        folder_name = folder_layers[-1]
    else:
        rel_path = ''
        folder_name = folder_path
    return rel_path, folder_name


def verify_list_event(source_type, folder):
    if source_type == 'Folder' and not folder:
        code = EAPIResponseCode.bad_request
        error_msg = 'missing folder name'
    elif source_type == 'Container' and folder:
        code = EAPIResponseCode.bad_request
        error_msg = 'Query project does not require folder name'
    else:
        code = EAPIResponseCode.success
        error_msg = ''
    return code, error_msg


def check_folder_exist(zone, project_code, folder):
    folder_check_event = {
        'namespace': zone,
        'project_code': project_code,
        'display_path': folder,
        'folder_name': folder.split('/')[-1],
        'folder_relative_path': '/'.join(folder.split('/')[0:-1])
    }
    folder_response = http_query_node_zone(folder_check_event)
    res = folder_response.json().get('result')
    if folder_response.status_code != 200:
        error_msg = folder_response.json()["error_msg"]
        code = EAPIResponseCode.internal_error
    elif res:
        error_msg = ''
        code = EAPIResponseCode.success
    else:
        error_msg = 'Folder not exist'
        code = EAPIResponseCode.not_found
    return code, error_msg


def get_hpc_jwt_token(token_issuer, username, password = None):
    _logger.info("get_hpc_jwt_token".center(80, '-'))
    try:
        payload = {
            "token_issuer": token_issuer,
            "username": username,
            "password": password
            }
        url = ConfigClass.HPC_SERVICE + "/v1/hpc/auth"
        _logger.info(f"Request url: {url}")
        res = requests.get(url, params=payload)
        _logger.info(f"Response: {res.text}")
        result = res.json().get('result')
        token = result.get('result').get('token')
    except Exception as e:
        _logger.error(e)
        token = ''
    finally:
        return token
    
def submit_hpc_job(job_submission_event) -> dict:
    _logger.info("submit_hpc_job".center(80, '-'))
    try:
        _logger.info(f"Received event: {job_submission_event}")
        token = job_submission_event.token
        host = job_submission_event.host
        username = job_submission_event.username
        job_info = job_submission_event.job_info
        job_script = job_info.get('script', '')
        _logger.info(f"Request job script: {job_script}")
        if not job_script:
            status_code = EAPIResponseCode.bad_request
            error_msg = 'Missing script'
            raise HPCError(status_code, error_msg)
        url = ConfigClass.HPC_SERVICE + "/v1/hpc/job"
        headers = {
            "Authorization": token
        }
        payload = {
            "slurm_host": host,
            "username": username,
            "job_info": job_info
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request payload: {payload}")
        res = requests.post(url, headers=headers, json=payload)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            raise HPCError(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e

def get_hpc_job_info(job_id, host, username, token) -> dict:
    _logger.info("get_hpc_job_info".center(80, '-'))
    try:
        _logger.info(f"Received job_id: {job_id}")
        url = ConfigClass.HPC_SERVICE + f"/v1/hpc/job/{job_id}"
        headers = {
            "Authorization": token
        }
        params = {
            "slurm_host": host,
            "username": username
        }
        _logger.info(f"Request url: {url}")
        _logger.info(f"Request headers: {headers}")
        _logger.info(f"Request params: {params}")
        res = requests.get(url, headers=headers, params=params)
        _logger.info(f"Response: {res.text}")
        response = res.json()
        status_code = response.get('code')
        if status_code == 200:
            result = response.get('result')
            return result
        else:
            error_msg = response.get('error_msg')
            if 'unknown job' in error_msg:
                error_msg = 'Job ID not found'
                status_code = EAPIResponseCode.not_found
                raise HPCError(status_code, error_msg)
            else:
                raise Exception(status_code, error_msg)
    except Exception as e:
        _logger.error(e)
        raise e
