import pytest
pytestmark = pytest.mark.asyncio


async def test_hpc_auth_should_return_200(test_async_client, httpx_mock):
    payload = {
            "token_issuer": 'host',
            "username": 'username',
            "password": 'password'
            }
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/auth',
        json={"result": {"token": "fake-token"}},
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post("/v1/hpc/auth", headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 200
    assert response['result'].get('token') == "fake-token"
    assert response.get('error_msg') == ""


async def test_hpc_auth_with_error_token_should_return_200(test_async_client, httpx_mock):
    payload = {
        "token_issuer": 'host',
        "username": 'username',
        "password": 'password'
    }
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/auth',
        json=None,
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post("/v1/hpc/auth", headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 500
    assert response['result'] == []
    assert response.get(
        'error_msg') == "Cannot authorized HPC: Cannot authorized HPC"


async def test_submit_hpc_job_should_return_200(test_async_client, httpx_mock):
    payload = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token",
        "job_info": {"job": {
            "name": "unit_test",
            "account": "sc-users"},
            "script": "sleep 300"}
    }
    test_api = "/v1/hpc/job"
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/job',
        json={"result": {"job_id": 15178},
              "code": 200},
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.post(test_api, headers=header, json=payload)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    assert response.get('result') == {"job_id": 15178}


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


async def test_hpc_get_job_success_should_return_200(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/job/12345"
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/12345?slurm_host=host&username=username&protocol=http',
        json={"result": {
            "job_id": "12345",
            "job_state": "COMPLETED",
            "standard_error": "",
            "standard_input": "",
            "standard_output": ""
        },
              "code": 200},
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 200
    assert response.get('error_msg') == ""
    result = response.get('result')
    assert result.get('job_id') == "12345"
    assert result.get('job_state') == "COMPLETED"


async def test_hpc_get_job_wrong_id_should_return_404(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/job/123"
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/123?slurm_host=host&username=username&protocol=http',
        json={"error_msg": "unknown job"},
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 404
    assert response.get('error_msg') == "Job ID not found"


async def test_hpc_list_nodes_should_return_200(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes?slurm_host=host&username=username&protocol=http',
        json={"result": [{"hostname1": {}}, {"hostname2": {}}],
              "code": 200},
        status_code=200,
    )
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


async def test_hpc_list_nodes_without_protocal_should_return_404(test_async_client, httpx_mock):
    params = {
        "host": "http",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/nodes"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


async def test_hpc_get_node_with_node_name_should_return_200(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes/fake_name?slurm_host=host&username=username&protocol=http',
        json={"result": [{"hostname1": {"cores": 42}}],
              "code": 200},
        status_code=200,
    )
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


async def test_hpc_get_node_without_node_name_should_return_404(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
    }
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes/fake_name?slurm_host=host&username=username&protocol=http',
        json={"error_msg": 'Invalid node name specified',
              "code": 404},
        status_code=404,
    )
    node_name = "fake_name"
    test_api = f"/v1/hpc/nodes/{node_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 404
    assert response.get('error_msg') == 'Node name not found'


async def test_hpc_list_partitions_should_return_200(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions?slurm_host=host&username=username&protocol=http',
        json={"result": [{"partition_name1": {"nodes": ["fake_node"]}}, {"partition_name2": {"nodes": ["fake_node2"]}}],
              "code": 200},
        status_code=200,
    )
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


async def test_hpc_list_partitions_without_protocal_should_return_400(test_async_client, mocker):
    params = {
        "host": "http",
        "username": "username",
        "token": "fake-hpc-token"
    }
    test_api = "/v1/hpc/partitions"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


async def test_hpc_get_partition_by_name_should_return_200(test_async_client, httpx_mock):
    params = {
        "host": "http://host",
        "username": "username",
        "token": "fake-hpc-token"
        }
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions/fake_name?slurm_host=host&username=username&protocol=http',
        json={"result": [{"partition_name1": {"nodes": ["fake_node"]}}],
              "code": 200},
        status_code=200,
    )
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


async def test_hpc_get_partition_by_name_without_protocal_should_return_400(test_async_client, mocker):
    params = {
        "host": "http",
        "username": "username",
        "token": "fake-hpc-token"
    }
    partition_name = "fake_name"
    test_api = f"/v1/hpc/partitions/{partition_name}"
    header = {'Authorization': 'fake token'}
    res = await test_async_client.get(test_api, headers=header, query_string=params)
    response = res.json()
    assert response.get('code') == 400
    assert response.get('error_msg') == "HPC protocal required"


