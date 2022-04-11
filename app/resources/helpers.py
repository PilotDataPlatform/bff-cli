import httpx
from ..config import ConfigClass
from ..models.base_models import EAPIResponseCode
from logger import LoggerFactory

_logger = LoggerFactory("Helpers").get_logger()


def get_zone(namespace):
    return {ConfigClass.GREEN_ZONE_LABEL.lower(): ConfigClass.GREEN_ZONE_LABEL,
            ConfigClass.CORE_ZONE_LABEL.lower(): ConfigClass.CORE_ZONE_LABEL
            }.get(namespace.lower(), ConfigClass.GREEN_ZONE_LABEL.lower())

async def batch_query_node_by_geid(geid_list):
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/query/geids"
    payload = {
        "geids": geid_list
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)
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


async def get_node(post_data, label):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/{label}/query", json=post_data)
        return response.json()
    except Exception:
        return None

async def get_user_projects(current_identity):
    _logger.info("get_user_projects".center(80, '-'))
    projects_list = []

    payload = {}

    if current_identity["role"] != "admin":
        roles = current_identity["realm_roles"]
        project_codes = list(set(i.split("-")[0] for i in roles))
        payload["code__in"] = project_codes

    async with httpx.AsyncClient() as client:
        response = await client.post(ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/Container/query", json=payload)
    for p in response.json():
        res_projects = {'name': p.get('name'),
                        'code': p.get('code'),
                        'id': p.get('id'),
                        'geid': p.get('global_entity_id')}
        projects_list.append(res_projects)
    _logger.info(f"Number of projects found: {len(projects_list)}")
    return projects_list


async def attach_manifest_to_file(event):
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
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, json=payload)
    _logger.info(f"RESPONSE: {response.text}")
    if not response.json():
        return None
    return response.json()

async def query_node(payload):
    _logger.info("query_node")
    _logger.info(f"query payload: {payload}")
    node_query_url = ConfigClass.NEO4J_SERVICE + "/v2/neo4j/nodes/query"
    async with httpx.AsyncClient() as client:
        response = await client.post(node_query_url, json=payload)
    _logger.info(f"query response: {response}")
    return response


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


async def query_relation(payload):
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/relations/query"
    _logger.info(f"Query file/folder payload: {payload}")
    _logger.info(f"Query file/folder API: {url}")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload)
        res = res.json()
        query_result = []
        for f in res:
            query_result.append(f.get('end_node'))
        result = query_result
        code = EAPIResponseCode.success
        error_msg = ''
        return code, result, error_msg
    except Exception as e:
        _logger.error(f"Error query files: {str(e)}")
        error_msg = str(e)
        code = EAPIResponseCode.internal_error
        return code, result, error_msg