import pytest
import jwt
import app.resources.dependencies
import time
from tests.helper import EAPIResponseCode
from app.models.project_models import POSTProjectFile
from app.resources.dependencies import *

project_code = "test_project"


@pytest.mark.asyncio
async def test_get_project_role_successed_should_project_role_and_200(mocker, httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "id": 1078,
            "global_entity_id": "fake_geid",
            "code": "test_project",
            "name": "test_project"
        }],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=123&end_id=1078',
        json=[
            {
                "r": {
                    "type": "collaborator",
                    "status": "active"
                }
            }
        ],
        status_code=200,
    )
    role, code = await get_project_role(123, project_code)
    print(role)
    print(code)
    assert role == "collaborator"
    assert code == EAPIResponseCode.success


@pytest.mark.asyncio
async def test_get_project_role_with_project_not_found_should_return_404(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[],
        status_code=200,
    )
    error_msg, code = await get_project_role("fake_id", "fake_code")
    assert error_msg == "Project not found"
    assert code == EAPIResponseCode.not_found


@pytest.mark.asyncio
async def test_get_project_role_with_user_not_found_should_return_403(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "id": 1078,
            "global_entity_id": "fake_geid",
            "code": "test_project",
            "name": "test_project"
        }],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=123&end_id=1078',
        json=[],
        status_code=200,
    )
    error_msg, code = await get_project_role(123, project_code)
    assert error_msg == 'User not in the project'
    assert code == EAPIResponseCode.forbidden


@pytest.mark.asyncio
async def test_jwt_required_should_return_successed(httpx_mock):
    mock_request = Request(scope={"type":"http"})
    encoded_jwt = jwt.encode(
        {"preferred_username": "test_user", "exp": time.time()+3}, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/User/query',
        json=[
            {
                "id": 1,
                "role": "admin"
            }
        ],
        status_code=200,
    )
    test_result = await jwt_required(mock_request)
    assert test_result["code"] == 200
    assert test_result["user_id"] == 1
    assert test_result["username"] == "test_user"


@pytest.mark.asyncio
async def test_jwt_required_without_token_should_return_unauthorized():
    mock_request = Request(scope={"type": "http"})
    mock_request._headers = {}
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 401


@pytest.mark.asyncio
async def test_jwt_required_with_token_expired_should_return_unauthorized():
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode(
        {"preferred_username": "test_user", "exp": time.time()-3}, key="unittest", algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 401


@pytest.mark.asyncio
async def test_jwt_required_with_neo4j_error_should_return_forbidden(httpx_mock):
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode(
        {"preferred_username": "test_user", "exp": time.time()+3}, key="unittest", algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/User/query',
        json="mock internal error",
        status_code=500,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


@pytest.mark.asyncio
async def test_jwt_required_with_user_not_in_neo4j_should_return_not_found(httpx_mock):
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode(
        {"preferred_username": "test_user", "exp": time.time()+3}, key="unittest", algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/User/query',
        json=[],
        status_code=200,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 404


@pytest.mark.asyncio
async def test_jwt_required_with_username_not_in_token_should_return_not_found(httpx_mock):
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode(
        {"preferred_username": None, "exp": time.time()+3}, key="unittest", algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/User/query',
        json=[
            {
                "id": 1,
                "role": "admin"
            }
        ],
        status_code=200,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 404


@pytest.mark.asyncio
async def test_check_permission_should_return_correct_permission(httpx_mock):
    event = {'user_id': 1,
             'username': "test_user",
             'role': "admin",
             'project_code': project_code,
             'zone': "gr"}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "id": 1078,
            "global_entity_id": "fake_geid",
            "code": "test_project",
            "name": "test_project"
        }],
        status_code=200,
    )
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=1&end_id=1078',
        json=[
            {
                "r": {
                    "type": "admin",
                    "status": "active"
                }
            }
        ],
        status_code=200,
    )
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/User/query',
        json=[{
            "global_entity_id": "fake_geid",
            "status": "active",
            "name": "test_user"
        }],
        status_code=200,
    )
    result = await check_permission(event)
    assert result == {'project_role': 'admin', 'project_code': 'test_project'}


@pytest.mark.asyncio
async def test_void_check_file_in_zone_should_return_bad_request(httpx_mock):
    mock_post_model = POSTProjectFile
    mock_post_model.type = "type"
    mock_post_model.zone = "gr"
    mock_file = {
        "resumable_relative_path": "relative_path",
        "resumable_filename": "file_name"
    }
    httpx_mock.add_response(
        method='GET',
        url='http://fileinfo_service/v1/project/test_project/file/exist/?type=type&zone=gr&file_relative_path=relative_path%2Ffile_name&project_code=test_project',
        json={"code": 200},
        status_code=200,
    )

    result = await void_check_file_in_zone(mock_post_model, mock_file, project_code)
    response = result.__dict__
    assert response['status_code'] == 400


@pytest.mark.asyncio
async def test_void_check_file_in_zone_with_external_service_error_should_return_forbidden():
    mock_post_model = POSTProjectFile
    mock_post_model.type = "type"
    mock_post_model.zone = "gr"
    mock_file = {
        "resumable_relative_path": "relative_path",
        "resumable_filename": "file_name"
    }
    result = await void_check_file_in_zone(mock_post_model, mock_file, project_code)
    response = result.__dict__
    assert response['status_code'] == 403


@pytest.mark.parametrize("test_zone, data_type", [("cr", "fake"), ("gr", "fake")])
def test_validate_upload_event_should_return_invalid_type(test_zone, data_type):
    result = validate_upload_event(test_zone, data_type)
    assert result == "Invalid Type"


def test_validate_upload_event_should_return_invalid_zone():
    result = validate_upload_event("zone")
    assert result == "Invalid Zone"


@pytest.mark.asyncio
async def test_transfer_to_pre_success(httpx_mock):
    mock_post_model = POSTProjectFile
    mock_post_model.current_folder_node = "current_folder_node"
    mock_post_model.operator = "operator"
    mock_post_model.upload_message = "upload_messagegr"
    mock_post_model.data = "data"
    mock_post_model.zone = "cr"
    mock_post_model.job_type = "job_type"
    httpx_mock.add_response(
        method='POST',
        url='http://data_upload_cr/v1/files/jobs',
        json={},
        status_code=200,
    )
    result = await transfer_to_pre(mock_post_model, project_code, "session_id")
    assert result.json() == {}


@pytest.mark.asyncio
async def test_transfer_to_pre_with_external_service_fail():
    mock_post_model = POSTProjectFile
    mock_post_model.current_folder_node = "current_folder_node"
    mock_post_model.operator = "operator"
    mock_post_model.upload_message = "upload_messagegr"
    mock_post_model.data = "data"
    mock_post_model.zone = "cr"
    mock_post_model.job_type = "job_type"
    result = await transfer_to_pre(mock_post_model, project_code, "session_id")
    response = result.__dict__
    assert response['status_code'] == 403
