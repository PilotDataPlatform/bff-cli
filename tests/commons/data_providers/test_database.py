import pytest

from sqlalchemy.future import create_engine


@pytest.fixture
def inmemory_engine():
    yield create_engine('sqlite:///:memory:', future=True)
