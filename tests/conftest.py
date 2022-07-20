# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient as TestAsyncClient
from fastapi import Request
from pydantic import BaseModel

from app.config import ConfigClass
from app.main import create_app
from app.resources.dependencies import jwt_required
from app.routers.v1.api_kg import APIProject


@pytest_asyncio.fixture
async def test_async_client():
    app = create_app()
    app.dependency_overrides[jwt_required] = jwt_required
    async with TestAsyncClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def test_async_client_auth():
    """Create client with mock auth token."""
    app = create_app()
    app.dependency_overrides[jwt_required] = override_jwt_required
    client = TestAsyncClient(app)
    return client


@pytest.fixture
def test_async_client_kg_auth():
    """Create client with mock auth token for kg api only."""
    from run import app
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = override_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


@pytest.fixture
def test_async_client_project_member_auth():
    """Create client with mock auth token for project api only."""
    from run import app
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = override_member_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


# Mock for the permission
async def override_jwt_required(request: Request):
    return {
        'code': 200,
        'user_id': 1,
        'username': 'testuser',
        'role': 'admin',
        'token': 'fake token',
        'realm_roles': ['platform-admin']
    }


async def override_member_jwt_required(request: Request):
    return {
        'code': 200,
        'user_id': 1,
        'username': 'testuser',
        'role': 'contributor',
        'token': 'fake token',
        'realm_roles': ['testproject-contributor']
    }


class HTTPAuthorizationCredentials(BaseModel):
    credentials: str = 'fake_token'


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(ConfigClass, 'KG_SERVICE', 'http://kg_service')
    monkeypatch.setattr(ConfigClass, 'AUDIT_TRAIL_SERVICE', 'http://audit_trail_service')
    monkeypatch.setattr(ConfigClass, 'GREEN_ZONE_LABEL', 'gr')
    monkeypatch.setattr(ConfigClass, 'CORE_ZONE_LABEL', 'cr')
    monkeypatch.setattr(ConfigClass, 'UPLOAD_SERVICE_CORE', 'http://data_upload_cr')
    monkeypatch.setattr(ConfigClass, 'UPLOAD_SERVICE_GREENROOM', 'http://data_upload_gr')
    monkeypatch.setattr(ConfigClass, 'HPC_SERVICE', 'http://service_hpc')
    monkeypatch.setattr(ConfigClass, 'AUTH_SERVICE', 'http://service_auth')
    monkeypatch.setattr(ConfigClass, 'METADATA_SERVICE', 'http://metadata_service')
    monkeypatch.setattr(ConfigClass, 'DATASET_SERVICE', 'http://dataset_service')
