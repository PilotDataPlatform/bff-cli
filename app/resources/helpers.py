import httpx
from ..config import ConfigClass
from logger import LoggerFactory

_logger = LoggerFactory("Helpers").get_logger()


def get_zone(namespace):
    return {ConfigClass.GREEN_ZONE_LABEL.lower(): 0,
            ConfigClass.CORE_ZONE_LABEL.lower(): 1
            }.get(namespace.lower(), 0)

async def batch_query_node_by_geid(geid_list):
    _logger.info("batch_query_node_by_geid".center(80, '-'))
    params = {
        'ids': geid_list
    }
    _logger.info(f"params: {params}")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            ConfigClass.METADATA_SERVICE + '/v1/items/batch/', 
            params=params, 
            follow_redirects=True
            )
    _logger.info(response.url)
    _logger.info(f"query response: {response.text}")
    res_json = response.json()
    _logger.info(f"res_json: {res_json}")
    result = res_json.get('result')
    located_geid = []
    query_result = {}
    for node in result:
        geid = node.get('id', '')
        archived = node.get('archived')
        # get file geid and archived status
        if geid in geid_list and archived == False:
            located_geid.append(geid)
            query_result[geid] = node
    # Returning valid geid list, incase archived or non-exist
    _logger.info(f"returning located_geid: {located_geid}")
    _logger.info(f"returning query_result: {query_result}")
    return located_geid, query_result


async def get_node(post_data, label):
    """
    get dataset node information
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ConfigClass.NEO4J_SERVICE + f"/v1/neo4j/nodes/{label}/query", 
                json=post_data
                )
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
        response = await client.post(
            ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/Container/query", 
            json=payload
            )
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
    file_type = event.get('file_type')
    _logger.info("attach_manifest_to_file".center(80, '-'))
    url = ConfigClass.METADATA_SERVICE + '/v1/items/batch/'
    if file_type == 'folder':
        params = {
                    'container_code': project_code,
                    'container_type': 'project',
                    'parent_id': global_entity_id,
                    'recursive': True,
                    'archived': False
                }
        _logger.info(f"Query node payload: {params}")
        folder_files = await query_node(params)
        ids_list = [geid for geid in folder_files.get('id')]
    else:
        ids_list = [global_entity_id]
    params = {
        'ids': ids_list
    }
    payload = {
        'attribute_template_id': manifest_id,
        'attributes': attributes
    }
    _logger.info(f"POSTING: {url}")
    _logger.info(f"PAYLOAD: {payload}")
    _logger.info(f"PARAMS: {params}")
    async with httpx.AsyncClient() as client:
        response = await client.put(url=url, params=params, json=payload)
    _logger.info(f"RESPONSE: {response.text}")
    if not response.json():
        return None
    return response.json()

# async def attach_manifest_to_file(event):
#     project_code = event.get('project_code')
#     global_entity_id = event.get('global_entity_id')
#     manifest_id = event.get('manifest_id')
#     attributes = event.get('attributes')
#     username = event.get('username')
#     project_role = event.get('project_role')
#     _logger.info("attach_manifest_to_file".center(80, '-'))
#     url = ConfigClass.FILEINFO_HOST + "/v1/files/attributes/attach"
#     payload = {
#         "project_code": project_code,
#         "manifest_id": manifest_id,
#         "global_entity_id": [global_entity_id],
#         "attributes": attributes,
#         "inherit": True,
#         "project_role": project_role,
#         "username": username
#                }
#     _logger.info(f"POSTING: {url}")
#     _logger.info(f"PAYLOAD: {payload}")
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url=url, json=payload)
#     _logger.info(f"RESPONSE: {response.text}")
#     if not response.json():
#         return None
#     return response.json()

async def query_node(payload):
    _logger.info("query_node".center(80, '-'))
    try:
        _logger.info(f"query params: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ConfigClass.METADATA_SERVICE + '/v1/items/search/', 
                params=payload, 
                follow_redirects=True
                )
        _logger.info(f"query response: {response.text}")
        return response
    except Exception as e:
        _logger.error(f'Error file/folder: {e}')


def separate_rel_path(folder_path):
    folder_layers = folder_path.strip('/').split('/')
    if len(folder_layers) > 1:
        rel_path = '/'.join(folder_layers[:-1])
        folder_name = folder_layers[-1]
    else:
        rel_path = ''
        folder_name = folder_path
    return rel_path, folder_name


# def verify_list_event(source_type, folder):
#     if source_type == 'Folder' and not folder:
#         code = EAPIResponseCode.bad_request
#         error_msg = 'missing folder name'
#     elif source_type == 'Container' and folder:
#         code = EAPIResponseCode.bad_request
#         error_msg = 'Query project does not require folder name'
#     else:
#         code = EAPIResponseCode.success
#         error_msg = ''
#     return code, error_msg

