import pytest
import app.resources.helpers
from app.resources.helpers import *
from tests.helper import EAPIResponseCode


def test_get_user_role_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=1&end_id=1086',
        json=[{"node":"fake_node"}],
        status_code=200,
    )
    result = get_user_role(1, 1086)
    assert result["node"] == "fake_node"


def test_get_user_role_failed():
    result = get_user_role(1, 1086)
    assert result == None


def test_query__node_has_relation_with_admin_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = query__node_has_relation_with_admin()
    assert result[0]["node"] == "fake_node"


def test_query__node_has_relation_with_admin_failed(httpx_mock):
    result = query__node_has_relation_with_admin()
    assert result == []


def test_query_node_has_relation_for_user_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = query_node_has_relation_for_user("test_user", "Container")
    assert result[0]["node"] == "fake_node"


def test_query_node_has_relation_for_user_failed():
    result = query_node_has_relation_for_user("test_user", "Container")
    assert result == []


def test_get_node_by_geid_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/nodes/geid/fake_geid',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = get_node_by_geid("fake_geid")
    assert result[0]["node"] == "fake_node"


def test_get_node_by_geid_failed():
    result = get_node_by_geid("fake_geid")
    assert result == None


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


def test_query_file_in_project_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": {"global_entity_id": "fake_geid"}
            },
        status_code=200,
    )
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result['code'] == 200


def test_query_file_in_project_return_empty(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": None
        },
        status_code=200,
    )
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


def test_query_file_in_project_return_failed():
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


def test_get_node_by_code_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "code": 200,
            "result": {}
        }],
        status_code=200,
    )
    result = get_node_by_code(123, "Container")
    assert result == {
        "code": 200,
        "result": {}
    }


def test_get_node_by_code_with_response_json_as_none(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=None,
        status_code=200,
    )
    result = get_node_by_code(123, "Container")
    assert result == None


def test_get_node_by_code_failed():
    result = get_node_by_code(123, "Container")
    assert result == None
