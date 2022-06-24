# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import httpx
from common import LoggerFactory
from common.project.project_client import ProjectClient

from ..config import ConfigClass

_logger = LoggerFactory('Helpers').get_logger()


def get_zone(namespace):
    return {
        ConfigClass.GREEN_ZONE_LABEL.lower(): 0,
        ConfigClass.CORE_ZONE_LABEL.lower(): 1,
    }.get(namespace.lower(), 0)


async def batch_query_node_by_geid(geid_list):
    _logger.info('batch_query_node_by_geid'.center(80, '-'))
    params = {'ids': geid_list}
    _logger.info(f'params: {params}')
    async with httpx.AsyncClient() as client:
        response = await client.get(
            ConfigClass.METADATA_SERVICE + '/v1/items/batch/',
            params=params,
            follow_redirects=True,
        )
    _logger.info(response.url)
    _logger.info(f'query response: {response.text}')
    res_json = response.json()
    _logger.info(f'res_json: {res_json}')
    result = res_json.get('result')
    located_geid = []
    query_result = {}
    for node in result:
        geid = node.get('id', '')
        archived = node.get('archived')
        # get file geid and archived status
        if geid in geid_list and not archived:
            located_geid.append(geid)
            query_result[geid] = node
    # Returning valid geid list, incase archived or non-exist
    _logger.info(f'returning located_geid: {located_geid}')
    _logger.info(f'returning query_result: {query_result}')
    return located_geid, query_result


async def get_dataset(dataset_code):
    """get dataset node information."""
    _logger.info('get_dataset'.center(80, '-'))
    try:
        url = ConfigClass.DATASET_SERVICE + f'/v1/dataset-peek/{dataset_code}'
        _logger.info(f'Getting dataset url: {url}')
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        _logger.info(f'Getting dataset response: {response.text}')
        result = response.json().get('result')
        return result
    except Exception:
        return None


async def list_datasets(user):
    """List all datasets."""
    try:
        payload = {
            'order_by': 'created_at',
            'page': 0,
            'page_size': 100,
            'filter': {},
            'order_type': 'desc'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ConfigClass.DATASET_SERVICE + f'/v1/users/{user}/datasets',
                json=payload
            )
        result = response.json().get('result')
        return result
    except Exception:
        return None


async def get_user_projects(current_identity):
    _logger.info('get_user_projects'.center(80, '-'))
    projects_list = []
    project_client = ProjectClient(
        ConfigClass.PROJECT_SERVICE, ConfigClass.REDIS_DB_URI
    )
    if current_identity['role'] != 'admin':
        roles = current_identity['realm_roles']
        project_codes = [i.split('-')[0] for i in roles]
        project_codes = ','.join(project_codes)
    else:
        project_codes = ''
    project_res = await project_client.search(code_any=project_codes)
    _logger.info(f'project_res: {project_res}')
    projects = project_res.get('result')
    _logger.info(f'projects: {projects}')
    for p in projects:
        res_projects = {'name': p.name, 'code': p.code, 'geid': p.id}
        projects_list.append(res_projects)
    _logger.info(f'Number of projects found: {len(projects_list)}')
    return projects_list


async def attach_manifest_to_file(event):
    global_entity_id = event.get('global_entity_id')
    manifest_id = event.get('manifest_id')
    attributes = event.get('attributes')
    _logger.info('attach_manifest_to_file'.center(80, '-'))
    url = ConfigClass.METADATA_SERVICE + '/v1/items/batch/bequeath/'
    params = {'ids': global_entity_id}
    payload = {'attribute_template_id': manifest_id, 'attributes': attributes}
    _logger.info(f'POSTING: {url}')
    _logger.info(f'PAYLOAD: {payload}')
    _logger.info(f'PARAMS: {params}')
    async with httpx.AsyncClient() as client:
        response = await client.put(url=url, params=params, json=payload)
    _logger.info(f'RESPONSE: {response.text}')
    if not response.json():
        return None
    return response.json()


async def query_file_folder(params):
    _logger.info('query_file_folder'.center(80, '-'))
    try:
        _logger.info(f'query params: {params}')
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ConfigClass.METADATA_SERVICE + '/v1/items/search/',
                params=params,
                follow_redirects=True,
            )
        _logger.info(f'query response: {response.url}')
        _logger.info(f'query response: {response.text}')
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
