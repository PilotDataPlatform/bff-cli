import pytest
import jwt
import time
from fastapi import Request
from app.models.project_models import POSTProjectFile
from app.resources.dependencies import get_project_role
from app.resources.dependencies import jwt_required
from app.resources.dependencies import has_permission
from app.resources.dependencies import check_file_exist
from app.resources.dependencies import validate_upload_event
from app.resources.dependencies import transfer_to_pre
from app.resources.error_handler import APIException
from app.config import ConfigClass

pytestmark = pytest.mark.asyncio
project_code = "test_project"



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
        url=f'http://service_auth/v1/admin/user?username=test_user',
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


async def test_jwt_required_without_token_should_return_unauthorized():
    mock_request = Request(scope={"type": "http"})
    mock_request._headers = {}
    with pytest.raises(APIException) as e:
        test_result = await jwt_required(mock_request)
        assert e.value.status_code == 401
        assert e.value.error_msg == "Token required"


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


async def test_jwt_required_with_neo4j_error_should_return_forbidden(httpx_mock):
    mock_request = Request(scope={"type": "http"})
    encoded_jwt = jwt.encode({
        "realm_access": {"roles": ["platform_admin"]},
        "preferred_username": "test_user",
        "exp": time.time()+3
    }, key="unittest" ,algorithm="HS256").decode('utf-8')
    mock_request._headers = {'Authorization': "Bearer " + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url='http://service_auth/v1/admin/user?username=test_user',
        json={ "result": {
        }},
        status_code=500,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


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
        url='http://service_auth/v1/admin/user?username=test_user',
        json={ "result": None},
        status_code=404,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


async def test_check_file_in_zone_should_return_bad_request(httpx_mock):
    zone = "gr"
    mock_file = {
        "resumable_relative_path": "relative_path",
        "resumable_filename": "file_name"
    }
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=test_project'
            '&container_type=project'
            '&parent_path=relative_path'
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&type=file'
            '&name=file_name'
            ),
        json={
            "code":200,
            "error_msg": "",
            "result": []},
        status_code=200,
    )
    result = await check_file_exist(zone, mock_file, project_code)
    assert result['code'] == 200


async def test_check_file_with_external_error_should_return_forbidden():
    mock_post_model = POSTProjectFile
    mock_post_model.type = "type"
    mock_post_model.zone = "gr"
    mock_file = {
        "resumable_relative_path": "relative_path",
        "resumable_filename": "file_name"
    }
    result = await check_file_exist(mock_post_model, mock_file, project_code)
    response = result.__dict__
    assert response['status_code'] == 403


@pytest.mark.parametrize("test_zone, data_type", [("cr", "fake"), ("gr", "fake")])
def test_validate_upload_event_should_return_invalid_type(test_zone, data_type):
    result = validate_upload_event(test_zone, data_type)
    assert result == "Invalid Type"


def test_validate_upload_event_should_return_invalid_zone():
    result = validate_upload_event("zone")
    assert result == "Invalid Zone"


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
