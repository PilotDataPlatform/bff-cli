from pydantic import BaseModel
import app.routers.v1.api_kg
import asyncio
import pytest
import pytest_asyncio
import os
import pdb

from datetime import datetime
from sqlalchemy import over, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateSchema, CreateTable
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from async_asgi_testclient import TestClient as TestAsyncClient
from fastapi import Request
from app.config import ConfigClass
from app.resources.dependencies import jwt_required
from app.commons.data_providers.database import DBConnection
from app.main import create_app
from app.routers.v1.api_kg import APIProject

from app.commons.data_providers.data_models import DataManifestModel
from app.commons.data_providers.data_models import DataAttributeModel
from app.commons.data_providers.data_models import DatasetVersionModel
from app.commons.data_providers.database import Base as ManifestBase
from app.commons.data_providers.database import Base as DatasetBase

os.environ['RDS_DB_URI'] = "test_container_uri"
RDS_SCHEMA_DEFAULT = os.environ['RDS_SCHEMA_DEFAULT']
print("test_rds")


@pytest.fixture(scope='session')
def db_postgres():
    with PostgresContainer('postgres:9.5') as postgres:
        yield postgres.get_connection_url().replace('+psycopg2', '+asyncpg')


@pytest_asyncio.fixture
async def engine(db_postgres):
    engine = create_async_engine(db_postgres)
    yield engine
    await engine.dispose()



@pytest_asyncio.fixture
async def test_async_client(db_postgres, engine):
    app = create_app()
    app.dependency_overrides[jwt_required] = jwt_required
    async with TestAsyncClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def test_async_client_auth(db_postgres, engine):
    '''
        Create client with mock auth token
    '''
    async with engine.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS {RDS_SCHEMA_DEFAULT};'))
    ConfigClass.RDS_DB_URI = db_postgres
    app = create_app()
    mock_session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    async def override_get_db():
        db = mock_session()
        try:
            yield db
        finally:
            await db.close()
    app.dependency_overrides[DBConnection.get_db] = override_get_db
    app.dependency_overrides[jwt_required] = override_jwt_required
    client = TestAsyncClient(app)
    return client


@pytest.fixture
def test_async_client_kg_auth():
    '''
        Create client with mock auth token for kg api only
    '''
    from run import app
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = override_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


@pytest.fixture
def test_async_client_project_member_auth():
    '''
        Create client with mock auth token for project api only
    '''
    from run import app
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = override_member_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop_policy(None)


@pytest_asyncio.fixture
async def create_db_dataset_metrics(engine):
    async with engine.begin() as conn:
        await conn.execute(CreateTable(DatasetVersionModel.__table__))
        await conn.run_sync(DatasetBase.metadata.create_all)
    async with AsyncSession(engine) as session:
        session.add(
            DatasetVersionModel(
                dataset_code="testdataset", dataset_geid="fake_geid", version="0",
                created_by="testuser", created_at=datetime(2022, 1, 9, 15, 11, 0), location="minio", notes="test123"
            )
        )
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(DatasetBase.metadata.drop_all)


@pytest_asyncio.fixture
async def create_db_manifest(engine):
    async with engine.begin() as conn:
        await conn.execute(CreateTable(DataManifestModel.__table__))
        await conn.run_sync(ManifestBase.metadata.create_all)
        await conn.execute(text('select * from test_schema.data_manifest'))
    async with AsyncSession(engine) as session:
        project_code = 'cli'
        session.add(DataManifestModel(
            name='fake_manifest', project_code=project_code))
        await session.commit()
        session.add(
            DataAttributeModel(
                manifest_id=1, name='fake_attribute', type='multiple_choice', value='1', project_code=project_code, optional=True
            )
        )
        session.add(
            DataAttributeModel(
                manifest_id=1, name='fake_attribute2', type='text', value=None, project_code=project_code, optional=True
            )
        )
        await session.commit()
    yield project_code
    async with engine.begin() as conn:
        # await conn.execute(text('DROP TYPE typeenum CASCADE'))
        await conn.run_sync(ManifestBase.metadata.drop_all)


# Mock for the permission
async def override_jwt_required(request: Request):
    return {
        "code": 200, 
        "user_id": 1, 
        "username": "testuser", 
        "role": "admin", 
        "token": "fake token"
    }


async def override_member_jwt_required(request: Request):
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


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, db_postgres):
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
    monkeypatch.setattr(
        ConfigClass, 'RDS_DB_URI',  f'{db_postgres}?prepared_statement_cache_size=0')
