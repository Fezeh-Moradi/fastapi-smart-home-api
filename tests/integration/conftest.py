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


@pytest.fixture
def patch_user_database(test_db):
    with patch(
        "services.user_service.users_collection",
        test_db.users,
    ):
        yield


@pytest.fixture
async def clean_test_database(test_db):
    await test_db.users.delete_many({})
    await test_db.devices.delete_many({})

    yield

    await test_db.users.delete_many({})
    await test_db.devices.delete_many({})


@pytest.fixture
def patch_device_database(test_db):
    with patch(
        "services.device_service.users_collection",
        test_db.users,
    ), patch(
        "services.device_service.devices_collection",
        test_db.devices,
    ):
        yield


@pytest.fixture
async def authenticated_user(
    client,
    test_db,
    patch_auth_database,
    patch_device_database,
):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Device Test User",
            "phone": "09111111111",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09111111111",
            "password": "123456",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    user = await test_db.users.find_one(
        {
            "phone": "09111111111"
        }
    )

    return {
        "user": user,
        "access_token": data["access_token"],
    }