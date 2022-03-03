import pytest
import app.resources.helpers
from app.resources.helpers import *
from tests.helper import EAPIResponseCode
from requests.models import Response


def test_batch_query_node_by_geid_successed(httpx_mock):
    geid_list = ["fake_geid"]
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={"result": [{"global_entity_id": "fake_geid"}]},
        status_code=200,
    )
    result_geid_list, query_node = batch_query_node_by_geid(geid_list)
    assert result_geid_list == geid_list
    assert query_node == {'fake_geid': {'global_entity_id': 'fake_geid'}}


def test_get_node_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json={
            "code": 200,
            "result": [{}]
        },
        status_code=200,
    )
    result = get_node(123, "Container")
    assert result == {
        "code": 200,
        "result": [{}]
    }


def test_get_node_with_response_json_as_none(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=None,
        status_code=200,
    )
    result = get_node(123, "Container")
    assert result == None


def test_get_node_by_code_failed():
    result = get_node(123, "Container")
    assert result == None


def test_attach_manifest_to_file_successed(httpx_mock):
    event = {
        'project_code':'project_code',
        'global_entity_id': 'geid',
        'manifest_id': 'mani_id',
        'attributes': 'attr',
        'username': 'test_user',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://fileinfo_service/v1/files/attributes/attach',
        json={"node": "fake_node"},
        status_code=200,
    )
    result = attach_manifest_to_file(event)
    assert result == {"node": "fake_node"}


def test_attach_manifest_to_file_failed(httpx_mock):
    event = {
        'project_code': 'project_code',
        'global_entity_id': 'geid',
        'manifest_id': 'mani_id',
        'attributes': 'attr',
        'username': 'test_user',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://fileinfo_service/v1/files/attributes/attach',
        json={},
        status_code=400,
    )
    result = attach_manifest_to_file(event)
    assert result == None


def test_query_node(httpx_mock):
    event = {
        'project_code': 'project_code',
        'namespace': 'gr',
        'folder_name': 'folder_name',
        'display_path': 'display_path',
        'folder_relative_path': 'folder_relative_path',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"node": "fake_node"},
        status_code=200,
    )
    result = query_node(event)
    assert result.json() == {"node": "fake_node"}


def test_separate_rel_path_with_namefolder():
    rel_path, folder_name = separate_rel_path("test_user/folder")
    assert rel_path == "test_user"
    assert folder_name == "folder"


def test_separate_rel_path_without_namefolder():
    rel_path, folder_name = separate_rel_path("test_user")
    assert rel_path == ""
    assert folder_name == "test_user"


@pytest.mark.parametrize("test_source, test_folder, expect_result",\
                         [("Folder", None, 'missing folder name'), 
                          ("Container", "test_user", 'Query project does not require folder name'),
                          ("Container", None, '')])
def test_verify_list_event(test_source, test_folder, expect_result):
    code, error_msg = verify_list_event(test_source, test_folder)
    assert error_msg == expect_result


def mock_query_node(arg1):
    mock_response = Response()
    if arg1['namespace'] == 'gr':
        mock_response.status_code = 200
        mock_response._content = b'{"result": "fake_node"}'
    elif arg1['folder_name'] == "not_exist_folder":
        mock_response.status_code = 200
        mock_response._content = b'{"result": []}'
    else:
        mock_response.status_code = 500
        mock_response._content = b'{ "error_msg" : "mock_error" }'
    return mock_response


def mock_query__node_has_relation_with_admin():
    return [{
        'name': 'test_user',
        'code':123,
        'id':'fake_id',
        'global_entity_id': 'geid'
    }]
