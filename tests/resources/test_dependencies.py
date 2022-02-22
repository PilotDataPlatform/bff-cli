import pytest
import jwt
import app.resources.dependencies
import time
from tests.helper import EAPIResponseCode
from app.models.project_models import POSTProjectFile
from app.resources.dependencies import *

project_code = "test_project"


def test_get_project_role_successed_should_project_role_and_200(mocker):
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node)
    mocker.patch.object(app.resources.dependencies,
                        "get_user_role", mock_user_role)
    role, code = get_project_role("fake_id", project_code)
    print(role)
    print(code)
    assert role == "collaborator"
    assert code == EAPIResponseCode.success


def test_get_project_role_with_project_not_found_should_return_404(mocker):
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node)
    error_msg, code = get_project_role("fake_id", "fake_code")
    assert error_msg == "Project not found"
    assert code == EAPIResponseCode.not_found


def test_get_project_role_with_user_not_found_should_return_403(mocker):
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node)
    mocker.patch.object(app.resources.dependencies,
                        "get_user_role", mock_user_role)
    error_msg, code = get_project_role("fake_user_id", project_code)
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


def test_check_permission_should_return_correct_permission(mocker):
    event = {'user_id': 1,
             'username': "test_user",
             'role': "admin",
             'project_code': project_code,
             'zone': "gr"}
    mocker.patch.object(app.resources.dependencies,
                        "get_project_role", mock_get_project_role)
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node_user)
    result = check_permission(event)
    assert result == {'project_role': 'admin', 'project_code': 'test_project'}


def test_check_permission_with_user_not_in_project_should_return_contributor_project_role(mocker):
    event = {'user_id': 1,
             'username': "test_user",
             'role': "contributor",
             'project_code': "fake_code",
             'zone': "gr"}
    mocker.patch.object(app.resources.dependencies,
                        "get_project_role", mock_get_project_role)
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node_user)
    result = check_permission(event)
    assert result["code"] == EAPIResponseCode.success
    assert result["result"] == "User not in the project"


def test_check_permission_with_project_not_found_should_return_project_not_found(mocker):
    event = {'user_id': 1,
             'username': "test_user",
             'role': "admin",
             'project_code': "fake_wrong_project",
             'zone': "gr"}
    mocker.patch.object(app.resources.dependencies,
                        "get_project_role", mock_get_project_role)
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node_user)
    result = check_permission(event)
    assert result["code"] == EAPIResponseCode.not_found
    assert result["result"] == {}


def test_check_permission_for_contributor_should_return_correct_permission(mocker):
    event = {'user_id': 2,
             'username': "test_user",
             'role': "contributor",
             'project_code': project_code,
             'zone': "gr"}
    mocker.patch.object(app.resources.dependencies,
                        "get_project_role", mock_get_project_role)
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node_user)
    result = check_permission(event)
    print(result)
    assert result == {'project_role': 'contributor',
                      'project_code': 'test_project', 
                      'uploader': 'test_user'}


def test_check_permission_for_contributor_in_core_should_return_forbidden(mocker):
    event = {'user_id': 2,
             'username': "test_user",
             'role': "contributor",
             'project_code': project_code,
             'zone': "cr"}
    mocker.patch.object(app.resources.dependencies,
                        "get_project_role", mock_get_project_role)
    mocker.patch.object(app.resources.dependencies,
                        "get_node", mock_get_node_user)
    result = check_permission(event)
    assert result["code"] == EAPIResponseCode.forbidden
    assert result["result"] == {}


def test_void_check_file_in_zone_should_return_bad_request(httpx_mock):
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

    result = void_check_file_in_zone(mock_post_model, mock_file, project_code)
    response = result.__dict__
    assert response['status_code'] == 400


def test_void_check_file_in_zone_with_external_service_error_should_return_forbidden(httpx_mock):
    mock_post_model = POSTProjectFile
    mock_post_model.type = "type"
    mock_post_model.zone = "gr"
    mock_file = {
        "resumable_relative_path": "relative_path",
        "resumable_filename": "file_name"
    }
    result = void_check_file_in_zone(mock_post_model, mock_file, project_code)
    response = result.__dict__
    assert response['status_code'] == 403


@pytest.mark.parametrize("test_zone, data_type", [("cr", "fake"), ("gr", "fake")])
def test_validate_upload_event_should_return_invalid_type(test_zone, data_type):
    result = validate_upload_event(test_zone, data_type)
    assert result == "Invalid Type"


def test_validate_upload_event_should_return_invalid_zone():
    result = validate_upload_event("zone")
    assert result == "Invalid Zone"


def test_transfer_to_pre_success(httpx_mock):
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
    result = transfer_to_pre(mock_post_model, project_code, "session_id")
    assert result.json() == {}


def test_transfer_to_pre_with_external_service_fail():
    mock_post_model = POSTProjectFile
    mock_post_model.current_folder_node = "current_folder_node"
    mock_post_model.operator = "operator"
    mock_post_model.upload_message = "upload_messagegr"
    mock_post_model.data = "data"
    mock_post_model.zone = "cr"
    mock_post_model.job_type = "job_type"
    result = transfer_to_pre(mock_post_model, project_code, "session_id")
    response = result.__dict__
    assert response['status_code'] == 403


def mock_get_project_role(arg1, arg2):
    if arg2 == "fake_code":
        return ("User not in the project", EAPIResponseCode.success)
    elif arg2 == "fake_wrong_project":
        return ("admin", EAPIResponseCode.not_found)
    if arg1 == 1:
        return ("admin", EAPIResponseCode.success)
    elif arg1 == 2:
        return ("contributor", EAPIResponseCode.success)



def mock_get_node(arg1, arg2):
    if arg1['code'] == project_code:
        return {"id": "test_project"}
    return None


def mock_user_role(arg1, arg2):
    mock_user_role_result = {
        "r": {
            "type": "collaborator",
            "status": "active"
        }
    }
    if arg1 == "fake_id":
        return mock_user_role_result
    return None


def mock_get_node_user(arg1, arg2):
    if arg1['name'] == "test_user":
        return {'status':'active'}
    return {'status': 'disabled'}
