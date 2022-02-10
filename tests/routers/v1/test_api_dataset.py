import pytest
from tests.logger import Logger
# To run particular test, edit the case_to_run_variable with following values:
# dataset list: list
# dataset detail: detail
# run all tests: '' or 'all'

case_to_run = ''

no_access_user_name = "jzhang53"
no_access_user_password = "Indoc1234567!"

log = Logger(name='test_create_resource_api.log')
test_dataset_api = "/v1/datasets"
dataset_code = "testdataset"
test_dataset_detailed_api = "/v1/dataset/testdataset"

@pytest.mark.asyncio
async def test_01_list_dataset_without_token(test_async_client):
    log.info('\n')
    log.info("test_01_list_dataset_without_token".center(80, '-'))
    log.info(f"GET API: {test_dataset_api}")
    res = await test_async_client.get(test_dataset_api)
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 401")
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

@pytest.mark.asyncio
async def test_02_list_dataset(test_async_client_auth, mocker):
    log.info('\n')
    log.info("test_02_list_dataset".center(80, '-'))
    log.info(f"GET API: {test_dataset_api}")
    mocker.patch('app.routers.v1.api_dataset.query_node_has_relation_for_user',\
         return_value=[{"end_node" :{"code": "testdataset"}}])
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    print(f"RESPONSE: {res.json()}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
    assert res_json.get('code') == 200
    datasets = []
    for d in res_json.get('result'):
        datasets.append(d.get('code'))
    assert dataset_code in datasets

@pytest.mark.asyncio
async def test_03_list_dataset_no_dataset(test_async_client_auth,mocker):
    log.info('\n')
    log.info("test_03_list_dataset_no_dataset".center(80, '-'))
    log.info(f"GET API: {test_dataset_api}")
    mocker.patch('app.routers.v1.api_dataset.query_node_has_relation_for_user',\
         return_value=[])
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
    assert res_json.get('code') == 200
    assert res_json.get('result') == []

@pytest.mark.asyncio
async def test_04_get_dataset_detail_without_token(test_async_client):
    log.info('\n')
    log.info("test_04_get_dataset_detail_without_token".center(80, '-'))
    log.info(f"GET API: {test_dataset_detailed_api}")
    res = await test_async_client.get(test_dataset_detailed_api)
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 401")
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required" 

@pytest.mark.asyncio
async def test_05_get_dataset_detail(test_async_client_auth, mocker):
    log.info('\n')
    log.info("test_05_get_dataset_detail".center(80, '-'))
    log.info(f"GET API: {test_dataset_detailed_api}")
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node_by_code',\
        return_value = {
            "labels": ["Dataset"],
            "global_entity_id": "fake_geid",
            "creator": "testuser",
            "modality": [],
            "code": "test0111"
            }
        )
    mocker.patch('app.routers.v1.api_dataset.RDConnection.get_dataset_versions',\
        mock_get_dataset_versions)
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)    
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
    assert res_json.get('code') == 200
    result = res_json.get('result')
    log.info(f"RESULT: {result}")
    _dataset_info = result.get('general_info')
    assert _dataset_info["creator"] == "testuser"
    _version_info = result.get('version_detail')
    log.info(f"Version detail: {_version_info}")
    assert _version_info[0]["dataset_code"] == dataset_code
    _version_no = result.get("version_no")
    assert _version_no == 1

@pytest.mark.asyncio
async def test_06_get_dataset_detail_no_access(test_async_client_auth, mocker):
    log.info('\n')
    log.info("test_04_get_dataset_detail_no_access".center(80, '-'))
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node_by_code',\
        return_value = {
            "labels": ["Dataset"],
            "global_entity_id": "fake_geid",
            "creator": "fakeuser",
            "modality": [],
            "code": "test0111"
            }
        )
    log.info(f"GET API: {test_dataset_detailed_api}")
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)    
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == "Permission Denied"

@pytest.mark.asyncio
async def test_08_get_dataset_detail_not_exist(test_async_client_auth, mocker):
    log.info('\n')
    log.info("test_05_get_dataset_detail_not_exist".center(80, '-'))
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node_by_code',\
        return_value = {
            "labels": ["None"],
            "global_entity_id": "fake_geid",
            "creator": "testuser",
            "modality": [],
            "code": "test0111"
            }
        )
    log.info(f"GET API: {test_dataset_detailed_api}")
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)  
    log.info(f"RESPONSE: {res.text}")
    res_json = res.json()
    log.info(f"COMPARING CODE: {res_json.get('code')}, 404")
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == "Cannot found given dataset code"


def mock_get_dataset_versions(arg1, arg2):
    mock_dataset_version = [
        {
            "dataset_code": dataset_code
        }
    ]
    return mock_dataset_version

