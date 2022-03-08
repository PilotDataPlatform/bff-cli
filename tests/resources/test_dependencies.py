import pytest
import jwt
import app.resources.dependencies
import time
from tests.helper import EAPIResponseCode
from app.models.project_models import POSTProjectFile
from app.resources.dependencies import *
from app.resources.error_handler import APIException
from app.config import ConfigClass

project_code = "test_project"



@pytest.mark.asyncio
async def test_jwt_required_should_return_successed(httpx_mock):
    mock_request = Request(scope={"type":"http"})
    encoded_jwt = jwt.encode({
        "realm_access": {"roles": ["platform_admin"]},
        "preferred_username": "test_user",
        "exp": time.time()+3
    }, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url=f'{ConfigClass.AUTH_SERVICE}/v1/admin/user?username=test_user',
        json={ "result": {
            "id": 1,
            "role": "admin"
        }},
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
    with pytest.raises(APIException) as e:
        test_result = await jwt_required(mock_request)
        assert e.value.status_code == 401
        assert e.value.error_msg == "Token required"


@pytest.mark.asyncio
async def test_jwt_required_with_token_expired_should_return_unauthorized():
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode({
        "realm_access": {"roles": ["platform_admin"]},
        "preferred_username": "test_user",
        "exp": time.time()-3
    }, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 401


@pytest.mark.asyncio
async def test_jwt_required_with_auth_error_should_return_forbidden(httpx_mock):
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode({
        "realm_access": {"roles": ["platform_admin"]},
        "preferred_username": "test_user",
        "exp": time.time()+3
    }, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url=f'{ConfigClass.AUTH_SERVICE}/v1/admin/user?username=test_user',
        json={ "result": {
        }},
        status_code=500,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


@pytest.mark.asyncio
async def test_jwt_required_with_username_not_in_token_should_return_not_found(httpx_mock):
    mock_request = Request(scope={"type": "http"})

    encoded_jwt = jwt.encode({
        "realm_access": {"roles": ["platform_admin"]},
        "preferred_username": "test_user",
        "exp": time.time()+3
    }, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url=f'{ConfigClass.AUTH_SERVICE}/v1/admin/user?username=test_user',
        json={ "result": None},
        status_code=404,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


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
