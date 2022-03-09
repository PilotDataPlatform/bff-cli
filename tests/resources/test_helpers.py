import pytest
import app.resources.helpers
from app.resources.helpers import get_user_role
from app.resources.helpers import query__node_has_relation_with_admin
from app.resources.helpers import query_node_has_relation_for_user
from app.resources.helpers import get_node_by_geid
from app.resources.helpers import batch_query_node_by_geid
from app.resources.helpers import query_file_in_project
from app.resources.helpers import get_node
from app.resources.helpers import get_user_projects
from app.resources.helpers import attach_manifest_to_file
from app.resources.helpers import http_query_node_zone
from app.resources.helpers import get_parent_label
from app.resources.helpers import separate_rel_path
from app.resources.helpers import verify_list_event
from app.resources.helpers import check_folder_exist
from requests.models import Response

pytestmark = pytest.mark.asyncio


async def test_get_user_role_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=1&end_id=1086',
        json=[
            {
                "p": {
                    "test_project": {
                        "id": 1,
                        "children": {
                            "test_user": {
                                "id": 1086,
                                "children": {}
                            }
                        }
                    }
                },
                "r": {
                    "type": "own"
                }
            }
        ],
        status_code=200,
    )
    result = await get_user_role(1, 1086)
    assert result["r"] == {"type": "own"}


async def test_get_user_role_failed():
    result = await get_user_role(1, 1086)
    assert result is None


async def test_query__node_has_relation_with_admin_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
                "id": 1078,
                "global_entity_id": "fake_geid",
                "code": "may10",
                "name": "MAY-10"
            }],
        status_code=200,
    )
    result = await query__node_has_relation_with_admin()
    assert result[0]["global_entity_id"] == "fake_geid"


async def test_query__node_has_relation_with_admin_failed(httpx_mock):
    result = await query__node_has_relation_with_admin()
    assert result == []


async def test_query_node_has_relation_for_user_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{
                "end_node": {
                    "id": 34673
                },
                "p": {
                    "amyguindoc14": {}
                },
                "r": {
                    "type": "admin",
                    "status": "active"
                },
                "start_node": {
                    "id": 4376
                }
            }
        ],
        status_code=200,
    )
    result = await query_node_has_relation_for_user("test_user", "Container")
    assert result[0]["r"] == {"type": "admin", "status": "active"}


async def test_query_node_has_relation_for_user_failed():
    result = await query_node_has_relation_for_user("test_user", "Container")
    assert result == []


async def test_get_node_by_geid_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/nodes/geid/fake_geid',
        json=[{
            "id": 4376, 
            "labels": ["User"],
            "global_entity_id": "fake_geid",
            "role": "admin"
            }],
        status_code=200,
    )
    result = await get_node_by_geid("fake_geid")
    assert result[0]["id"] == 4376


async def test_get_node_by_geid_failed():
    result = await get_node_by_geid("fake_geid")
    assert result is None


async def test_batch_query_node_by_geid_successed(httpx_mock):
    geid_list = ["fake_geid"]
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={"result": [{"global_entity_id": "fake_geid"}]},
        status_code=200,
    )
    result_geid_list, query_node = await batch_query_node_by_geid(geid_list)
    assert result_geid_list == geid_list
    assert query_node == {'fake_geid': {'global_entity_id': 'fake_geid'}}


async def test_query_file_in_project_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": [{"global_entity_id": "fake_geid"}]
            },
        status_code=200,
    )
    result = await query_file_in_project("test_project", "testfolder/testfile")
    assert result['code'] == 200


async def test_query_file_in_project_return_empty(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": []
        },
        status_code=200,
    )
    result = await query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


async def test_query_file_in_project_return_failed():
    result = await query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


async def test_get_node_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "code": 200,
            "result": {}
        }],
        status_code=200,
    )
    result = await get_node(123, "Container")
    assert result == {
        "code": 200,
        "result": {}
    }


async def test_get_node_with_response_json_as_none(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=None,
        status_code=200,
    )
    result = await get_node(123, "Container")
    assert result is None


async def test_get_node_by_code_failed():
    result = await get_node(123, "Container")
    assert result is None


async def test_get_user_admin_projects_successed(mocker):
    mocker.patch.object(app.resources.helpers,
                        "query__node_has_relation_with_admin", mock_query__node_has_relation_with_admin)
    result = await get_user_projects('admin', 'test_user')
    assert result[0]['name'] == 'test_user'
    assert result[0]['code'] == 123


async def test_get_user_project_user_projects_successed(mocker):
    mocker.patch.object(app.resources.helpers,
                        "query_node_has_relation_for_user", mock_query_node_has_relation_for_user)
    result = await get_user_projects('contributor', 'test_user')
    assert result[0]['name'] == 'test_user'
    assert result[0]['code'] == 123


async def test_attach_manifest_to_file_successed(httpx_mock):
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
        json={
            "code": 200,
            "error_msg": "",
            "result": {
                "operation_status": "SUCCEED"
            }
        },
        status_code=200,
    )
    result = await attach_manifest_to_file(event)
    assert result["result"] == {
        "operation_status": "SUCCEED"
    }


async def test_attach_manifest_to_file_failed(httpx_mock):
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
    result = await attach_manifest_to_file(event)
    assert result is None


async def test_http_query_node_zone(httpx_mock):
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
        json={"result": [{"labels": ["zone", "Folder"],
                          "project_code": "test_project", "name": "fake_folder"}]},
        status_code=200,
    )
    result = await http_query_node_zone(event)
    assert result.json() == {"result": [{"labels": ["zone", "Folder"],
                                         "project_code": "test_project", "name": "fake_folder"}]}


@pytest.mark.parametrize("test_source, expect_result", [("folder", "Folder"), ("container", "Container"), ("File", None)])
def test_get_parent_label(test_source, expect_result):
    result = get_parent_label(test_source)
    assert result == expect_result


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


@pytest.mark.parametrize("test_zone, folder, expect_result",
                         [("gr", "test_user/folder", ''),
                          ("zone", "test_user/folder", 'mock_error'),
                          ("cr", "test_user/not_exist_folder", 'Folder not exist')])
async def test_check_folder_exist(mocker, test_zone, folder, expect_result):
    mocker.patch.object(app.resources.helpers,
                        "http_query_node_zone", mock_http_query_node_zone)
    code, error_msg = await check_folder_exist(test_zone, "test_project", folder)
    assert error_msg == expect_result


async def mock_http_query_node_zone(arg1):
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


async def mock_query__node_has_relation_with_admin():
    return [{
        'name': 'test_user',
        'code':123,
        'id':'fake_id',
        'global_entity_id': 'geid'
    }]


async def mock_query_node_has_relation_for_user(arg1):
    return [{'r': {'status':'active'}, 'end_node': {'name': 'test_user',
                                                       'code': 123,
                                                       'id': 'fake_id',
                                                       'global_entity_id': 'geid'}}]
