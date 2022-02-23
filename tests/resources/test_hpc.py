import pytest
from app.resources.hpc import *
from app.models.hpc_models import HPCJobSubmitPost


def test_get_hpc_jwt_token_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/auth',
        json={"result": "hpc_token"},
        status_code=200,
    )
    result = get_hpc_jwt_token("issuer", "username", "pwd")
    assert result == "hpc_token"


def test_get_hpc_jwt_token_failed(httpx_mock):
    result = get_hpc_jwt_token("issuer", "username", "pwd")
    assert result == ''


def test_submit_hpc_job_successed(httpx_mock):
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'http://hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': 'script'}
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/job',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = submit_hpc_job(mock_request)
    assert result == "hpc"


def test_submit_hpc_job_with_hpc_host_without_protocal():
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': 'script'}
    try:
        submit_hpc_job(mock_request)
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_submit_hpc_job_without_job_script():
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'http://hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': ''}
    try:
        submit_hpc_job(mock_request)
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_submit_hpc_job_with_job_error(httpx_mock):
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'http://hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': 'script'}
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/job',
        json={"error_msg": "mock error",
              "code": 400},
        status_code=400,
    )
    try:
        submit_hpc_job(mock_request)
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_submit_hpc_job_with_job_token_expired(httpx_mock):
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'http://hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': 'script'}
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/job',
        json={"error_msg": "Zero Bytes were transmitted or received",
              "code": 500},
        status_code=500,
    )
    try:
        submit_hpc_job(mock_request)
    except HPCError as e:
        assert e.code == EAPIResponseCode.forbidden


def test_submit_hpc_job_with_job_token_expired(httpx_mock):
    mock_request = HPCJobSubmitPost
    mock_request.token = 'token'
    mock_request.host = 'http://hpc_host'
    mock_request.username = 'user'
    mock_request.job_info = {'script': 'script'}
    httpx_mock.add_response(
        method='POST',
        url='http://service_hpc/v1/hpc/job',
        json={"error_msg": "mock fobidden",
              "code": 403},
        status_code=403,
    )
    try:
        submit_hpc_job(mock_request)
    except HPCError as e:
        assert e.code == EAPIResponseCode.internal_error


def test_get_hpc_job_info_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = get_hpc_job_info(123, "http://hpc_host", "test_user", "token")
    assert result == "hpc"


def test_get_hpc_job_info_with_hpc_host_error(httpx_mock):
    try:
        get_hpc_job_info(123, "hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_job_info_with_job_id_not_found(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "unknown job"},
        status_code=400,
    )
    try:
        get_hpc_job_info(123, "http://hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.not_found


def test_get_hpc_job_info_with_request_url_not_found(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "Unable find requested URL"},
        status_code=400,
    )
    try:
        get_hpc_job_info(123, "http://hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.not_found


def test_get_hpc_job_info_with_request_url_not_found(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/job/123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "mock error",
              "code": 500},
        status_code=500,
    )
    try:
        get_hpc_job_info(123, "http://hpc_host", "test_user", "token")
    except Exception as e:
        assert str(e) == "(500, 'mock error')"


def test_get_hpc_nodes_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = get_hpc_nodes("http://hpc_host", "test_user", "token")
    assert result == "hpc"


def test_get_hpc_nodes_hpc_host_error(httpx_mock):
    try:
        get_hpc_nodes("hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_nodes_failed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "mock error",
              "code": 500},
        status_code=500,
    )
    try:
        get_hpc_nodes("http://hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.internal_error


def test_get_hpc_node_by_name_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes/node123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = get_hpc_node_by_name(
        "http://hpc_host", "test_user", "token", "node123")
    assert result == "hpc"


def test_hpc_node_by_name_hpc_host_error():
    try:
        get_hpc_node_by_name("hpc_host", "test_user", "token", "node123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_node_by_name_failed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes/node123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "Invalid node name specified",
              "code": 400},
        status_code=400,
    )
    try:
        get_hpc_node_by_name(
            "http://hpc_host", "test_user", "token", "node123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.not_found


def test_get_hpc_node_by_name_failed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/nodes/node123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "mock error",
              "code": 400},
        status_code=400,
    )
    try:
        get_hpc_node_by_name(
            "http://hpc_host", "test_user", "token", "node123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.internal_error


def test_get_hpc_partitions_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = get_hpc_partitions("http://hpc_host", "test_user", "token")
    assert result == "hpc"


def test_get_hpc_partitions_hpc_host_error():
    try:
        get_hpc_partitions("hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_partitions_retrieval_failed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "Retrieval of HPC partitions info failed",
              "code": 400},
        status_code=400,
    )
    try:
        get_hpc_partitions("http://hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_partitions_internal_failed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "mock error",
              "code": 500},
        status_code=500,
    )
    try:
        get_hpc_partitions("http://hpc_host", "test_user", "token")
    except HPCError as e:
        assert e.code == EAPIResponseCode.internal_error


def test_get_hpc_partition_by_name_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions/parti123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"result": "hpc",
              "code": 200},
        status_code=200,
    )
    result = get_hpc_partition_by_name(
        "http://hpc_host", "test_user", "token", "parti123")
    assert result == "hpc"


def test_get_hpc_partition_by_name_hpc_host_error():
    try:
        get_hpc_partition_by_name("hpc_host", "test_user", "token", "parti123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.bad_request


def test_get_hpc_partition_by_name_with_partition_not_found(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions/parti123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "Invalid partition name specified",
              "code": 400},
        status_code=400,
    )
    try:
        get_hpc_partition_by_name(
        "http://hpc_host", "test_user", "token", "parti123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.not_found


def test_get_hpc_partition_by_name_with_internal_error(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://service_hpc/v1/hpc/partitions/parti123?slurm_host=hpc_host&username=test_user&protocol=http',
        json={"error_msg": "mock error",
              "code": 500},
        status_code=500,
    )
    try:
        get_hpc_partition_by_name(
            "http://hpc_host", "test_user", "token", "parti123")
    except HPCError as e:
        assert e.code == EAPIResponseCode.internal_error
