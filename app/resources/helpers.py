import os
import zipfile
import time
import json
import enum
from ..config import ConfigClass
from ..commons.data_providers.redis import SrvRedisSingleton
import requests
from ..models.base_models import APIResponse, EAPIResponseCode

def get_user_role(username, api_response):
    url = ConfigClass.NEO4J_SERVICE + "nodes/User/query"
    res = requests.post(
        url=url,
        json={"name": username}
    )
    users = json.loads(res.text)
    if (len(users) == 0):
        api_response.error_msg = "token expired"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
    user_role = users[0]['role']
    return user_role


#######################################################
def generate_zipped_file_path(project_code):
    '''
    generate zipped file path
    '''
    target_path = os.path.join(
        ConfigClass.NFS_ROOT_PATH, project_code, 'workdir')  # data/vre-storage/project_code/workdir
    zip_filename = project_code + '_zipped' + \
        '_' + str(int(time.time())) + '.zip'
    zipped_file_path = os.path.join(target_path, zip_filename)
    return zipped_file_path


def zip_multi_files(zipped_file_path, target_files):
    '''
    zip multiple files
    '''
    target_path = os.path.dirname(zipped_file_path)
    if not os.path.isdir(target_path):
        try:
            os.makedirs(target_path)
        except FileExistsError as file_e:
            # ignore existed folder
            pass
    try:
        with zipfile.ZipFile(zipped_file_path, 'w', zipfile.ZIP_STORED) as zf:
            for f in target_files:
                full_path = f["full_path"]
                if not os.path.exists(full_path):
                    return False, 'File not found: %s' % full_path
                with open(full_path, 'rb') as fp:
                    zf.writestr(full_path, fp.read())
    except Exception as e:
        return False, str(e)

    return True, zipped_file_path


def namespace_to_path(my_disk_namespace: str):
    '''
    disk namespace to path
    '''
    return {
        "greenroom": ConfigClass.NFS_ROOT_PATH,
        "vrecore": ConfigClass.VRE_ROOT_PATH
    }.get(my_disk_namespace, None)


def set_status(session_id, job_id, source, action, target_status,
               project_code, operator, payload=None, progress=0):
    '''
    set session job status
    '''
    srv_redis = SrvRedisSingleton()
    my_key = "dataaction:{}:{}:{}:{}:{}:{}".format(
        session_id, job_id, action, project_code, operator, source)
    record = {
        "session_id": session_id,
        "job_id": job_id,
        "source": source,
        "action": action,
        "status": target_status,
        "project_code": project_code,
        "operator": operator,
        "progress": progress,
        "payload": payload,
        'update_timestamp': str(round(time.time()))
    }
    my_value = json.dumps(record)
    srv_redis.set_by_key(my_key, my_value)
    return record


def get_status(session_id, job_id, project_code, action, operator=None):
    '''
    get session job status from datastore
    '''
    srv_redis = SrvRedisSingleton()
    my_key = "dataaction:{}:{}:{}:{}".format(
        session_id, job_id, action, project_code)
    if operator:
        my_key = "dataaction:{}:{}:{}:{}:{}".format(
            session_id, job_id, action, project_code, operator)
    res_binary = srv_redis.mget_by_prefix(my_key)
    return [json.loads(record.decode('utf-8')) for record in res_binary] if res_binary else []
