import pytest

from fastapi.testclient import TestClient
from async_asgi_testclient import TestClient as TestAsyncClient
from fastapi import Request
from app.config import ConfigClass
from app.resources.dependencies import jwt_required
from run import app
from enum import Enum

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
    client = TestAsyncClient(app)
    app.dependency_overrides[jwt_required] = overide_jwt_required
    return client

async def overide_jwt_required(request: Request):
    return {
        "code": 200, 
        "user_id": 1, 
        "username": "testuser", 
        "role": "admin", 
        "token": "fake token"
    }

class EAPIResponseCode(Enum):
    success = 200
    internal_error = 500
    bad_request = 400
    not_found = 404
    forbidden = 403
    unauthorized = 401
    conflict = 409

# @pytest.fixture(autouse=True)
# def mock_settings(monkeypatch):
    # monkeypatch.setattr(ConfigClass, 'AUTH_SERVICE', 'http://auth_service')
    # monkeypatch.setattr(ConfigClass, 'BBN_ORG', 'test_org')
    # monkeypatch.setattr(ConfigClass, 'BBN_ENDPOINT', 'http://10.3.7.220/kg/v1')
    # monkeypatch.setattr(ConfigClass, 'env', 'test')