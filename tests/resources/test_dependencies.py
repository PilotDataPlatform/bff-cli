import pytest
from pytest_httpx import HTTPXMock
from tests.logger import Logger

log = Logger(name='test_dependencies.log')

@pytest.mark.asyncio
async def test_jwt_required(test_async_client):
    pass

