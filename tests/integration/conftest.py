import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from config import settings


@pytest.fixture
async def test_db():
    client = AsyncIOMotorClient(
        settings.MONGO_URL
    )

    database = client["smart_home_test"]

    yield database

    client.close()


@pytest.fixture
async def clean_test_database(test_db):
    await test_db.users.delete_many({})

    yield

    await test_db.users.delete_many({})


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def patch_auth_database(test_db):
    with patch(
        "routers.auth.users_collection",
        test_db.users,
    ):
        yield