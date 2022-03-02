from pydantic import BaseModel
import app.routers.v1.api_kg
import asyncio
import pytest

from fastapi.testclient import TestClient
from async_asgi_testclient import TestClient as TestAsyncClient
from fastapi import Request
from app.config import ConfigClass
from app.resources.dependencies import jwt_required
from run import app
from app.routers.v1.api_kg import APIProject
from starlette.config import environ
# from testcontainers.postgres import PostgresContainer


# @pytest.fixture(scope='session')
# def db_postgres():
#     with PostgresContainer("postgres:9.5") as postgres:
#         yield postgres.get_connection_url().replace('+psycopg2', '+asyncpg')


# @pytest_asyncio.fixture
# async def engine(db_postgres):
#     engine = create_async_engine(db_postgres)
#     yield engine
#     await engine.dispose()

environ['NEO4J_SERVICE'] = 'http://neo4j_service'


@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_async_client():
    client = TestAsyncClient(app)
    app.dependency_overrides[jwt_required] = jwt_required
    return client

@pytest.fixture
def test_async_client_auth():
    '''
        Create client with mock auth token
    '''
    app.dependency_overrides[jwt_required] = overide_jwt_required
    client = TestAsyncClient(app)
    return client


@pytest.fixture
def test_async_client_kg_auth():
    '''
        Create client with mock auth token for kg api only
    '''
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = overide_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


@pytest.fixture
def test_async_client_project_member_auth():
    '''
        Create client with mock auth token for kg api only
    '''
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = overide_member_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


async def overide_jwt_required(request: Request):
    return {
        "code": 200, 
        "user_id": 1, 
        "username": "testuser", 
        "role": "admin", 
        "token": "fake token"
    }


async def overide_member_jwt_required(request: Request):
    return {
        "code": 200,
        "user_id": 1,
        "username": "testuser",
        "role": "contributor",
        "token": "fake token"
    }

class HTTPAuthorizationCredentials(BaseModel):
    credentials: str = 'fake_token'


@pytest.fixture
def mock_query__node_has_relation_with_admin(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://10.3.7.216:5062/v1/neo4j/nodes/Container/query',
        json=[{"node": "fake_node"}],
        status_code=200,
    )


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop_policy(None)



@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(ConfigClass, 'NEO4J_SERVICE', 'http://neo4j_service')
    monkeypatch.setattr(ConfigClass, 'FILEINFO_HOST', 'http://fileinfo_service')
    monkeypatch.setattr(ConfigClass, 'KG_SERVICE', 'http://kg_service')
    monkeypatch.setattr(ConfigClass, 'PROVENANCE_SERVICE',
                        'http://provenance_service')
    monkeypatch.setattr(ConfigClass, 'GREEN_ZONE_LABEL', 'gr')
    monkeypatch.setattr(ConfigClass, 'CORE_ZONE_LABEL', 'cr')
    monkeypatch.setattr(ConfigClass, 'DATA_UPLOAD_SERVICE_CORE',
                        'http://data_upload_cr')
    monkeypatch.setattr(
        ConfigClass, 'DATA_UPLOAD_SERVICE_GREENROOM', 'http://data_upload_gr')
    monkeypatch.setattr(
        ConfigClass, 'HPC_SERVICE', 'http://service_hpc')
