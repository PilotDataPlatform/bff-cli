from sre_constants import IN
import pytest
from unittest.mock import patch
from app.models.error_model import HPCError
from tests.helper import EAPIResponseCode


@pytest.mark.asyncio
async def test_hpc_auth_should_return_200(test_async_client, mocker):
    payload = {
            "token_issuer": 'host',
            "username": 'username',
            "password": 'password'
            }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_jwt_token',
                 return_value={"token": "fake-token"})
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post("/v1/hpc/auth", headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 200
    assert response['result'].get('token') == "fake-token"
    assert response.get('error_msg') == ""


@pytest.mark.asyncio
async def test_hpc_auth_with_error_token_should_return_200(test_async_client, mocker):
    payload = {
        "token_issuer": 'host',
        "username": 'username',
        "password": 'password'
    }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_jwt_token',
                 return_value="")
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post("/v1/hpc/auth", headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 500
    assert response['result'] == []
    assert response.get(
        'error_msg') == "Cannot authorized HPC: Cannot authorized HPC"


@pytest.mark.asyncio
async def test_submit_hpc_job_should_return_200(test_async_client, mocker):
    payload = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token",
        "job_info": { "job": {
            "name": "unit_test",
            "account": "sc-users"},
            "script": "sleep 300" }
    }
    test_api = "/v1/hpc/job"
    mocker.patch('app.routers.v1.api_hpc.submit_hpc_job',
                 return_value={"job_id": 15178})
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post(test_api, headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    assert response.get('result') == {"job_id": 15178}


@pytest.mark.asyncio
async def test_submit_hpc_job_without_script_should_return_400(test_async_client):
    payload = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token",
        "job_info": {}
    }
    test_api = "/v1/hpc/job"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post(test_api, headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == 'Missing script'
    assert response.get('result') == {}


@pytest.mark.asyncio
async def test_hpc_get_job_success_should_return_200(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/job/%s".format('12345')
    mocker.patch('app.routers.v1.api_hpc.get_hpc_job_info',
                 return_value={
                     "job_id": "12345", 
                     "job_state": "COMPLETED", 
                     "standard_error": "", 
                     "standard_input": "", 
                     "standard_output": ""
                     }
                )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result = response.get('result')
    assert result.get('job_id') == "12345"
    assert result.get('job_state') == "COMPLETED"


@pytest.mark.asyncio
async def test_hpc_get_job_wrong_id_should_return_404(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/job/%s".format('123')
    mocker.patch('app.routers.v1.api_hpc.get_hpc_job_info',
                 side_effect=HPCError(
                     EAPIResponseCode.not_found, 'Job ID not found')
                )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 404
    assert response.get('error_msg') == "Job ID not found"


@pytest.mark.asyncio
async def test_hpc_list_nodes_should_return_200(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_nodes',
                 return_value=[{"hostname1": {}}, {"hostname2": {}}])
    test_api = "/v1/hpc/nodes"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result =  response.get('result')
    exp_node1 = {"hostname1":{}}
    exp_node2 = {"hostname2":{}}
    assert exp_node1 in result
    assert exp_node2 in result


@pytest.mark.asyncio
async def test_hpc_list_nodes_without_protocal_should_return_404(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_nodes',
                 side_effect=HPCError(
                     EAPIResponseCode.bad_request, "HPC protocal required"))
    test_api = "/v1/hpc/nodes"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


@pytest.mark.asyncio
async def test_hpc_get_node_with_noe_name_should_return_200(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_node_by_name',
                 return_value=[{"hostname1": {"cores": 42}}])
    node_name = "fake_name"
    test_api = f"/v1/hpc/nodes/{node_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result = response.get('result')
    exp_node1 = {"hostname1":{"cores":42}}
    assert  exp_node1 in result


@pytest.mark.asyncio
async def test_hpc_get_node_without_node_name_should_return_404(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_node_by_name',
                 side_effect=HPCError(EAPIResponseCode.not_found, 'Node name not found'))
    node_name = "fake_name"
    test_api = f"/v1/hpc/nodes/{node_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 404
    assert response.get('error_msg') == 'Node name not found'


@pytest.mark.asyncio
async def test_hpc_list_partitions_should_return_200(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_partitions',
                 return_value=[{"partition_name1": {"nodes": ["fake_node"]}}, {"partition_name2": {"nodes": ["fake_node2"]}}])
    test_api = "/v1/hpc/partitions"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result = response.get('result')
    exp_partition1 = {"partition_name1": {"nodes": ["fake_node"]}}
    exp_partition2 = {"partition_name2": {"nodes": ["fake_node2"]}}
    assert exp_partition1 in result
    assert exp_partition2 in result


@pytest.mark.asyncio
async def test_hpc_list_partitions_without_protocal_should_return_400(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_partitions',
                 side_effect=HPCError(EAPIResponseCode.bad_request, "HPC protocal required"))
    test_api = "/v1/hpc/partitions"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


@pytest.mark.asyncio
async def test_hpc_get_partition_by_name_should_return_200(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_partition_by_name',
                 return_value=[{"partition_name1": {"nodes": ["fake_node"]}}])
    partition_name = "fake_name"
    test_api = f"/v1/hpc/partitions/{partition_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result = response.get('result')
    exp_partition1 = {"partition_name1": {"nodes": ["fake_node"]}}
    assert exp_partition1 in result


@pytest.mark.asyncio
async def test_hpc_get_partition_by_name_without_protocal_should_return_400(test_async_client, mocker):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    mocker.patch('app.routers.v1.api_hpc.get_hpc_partition_by_name',
                 side_effect=HPCError(EAPIResponseCode.bad_request, "HPC protocal required"))
    partition_name = "fake_name"
    test_api = f"/v1/hpc/partitions/{partition_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


