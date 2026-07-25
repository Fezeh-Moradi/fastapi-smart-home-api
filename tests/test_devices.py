import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from fastapi.testclient import TestClient

from main import app
from core.security import create_access_token


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_device_service_collections():
    with (
        patch("services.device_service.devices_collection") as mock_devices,
        patch("services.device_service.users_collection") as mock_users,
    ):
        mock_users.find_one = AsyncMock()

        mock_devices.find_one = AsyncMock()
        mock_devices.insert_one = AsyncMock()
        mock_devices.update_one = AsyncMock()
        mock_devices.delete_one = AsyncMock()
        mock_devices.count_documents = AsyncMock()
        mock_devices.aggregate = MagicMock()

        yield mock_devices, mock_users


@pytest.fixture
def user_id():
    return ObjectId()


@pytest.fixture
def device_id():
    return ObjectId()


@pytest.fixture
def auth_token(user_id):
    return create_access_token(
        {
            "user_id": str(user_id)
        }
    )


@pytest.fixture
def user_document(user_id):
    return {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }


@pytest.fixture
def device_document(device_id, user_id):
    return {
        "_id": device_id,
        "name": "Living Room Sensor",
        "device_type": "sensor",
        "serial_number": "SN-123456",
        "status": "active",
        "is_online": False,
        "owner_id": user_id,
    }

def test_create_device(
    client,
    mock_device_service_collections,
    user_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = None

    mock_devices.insert_one.return_value.inserted_id = ObjectId()

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.post(
        "/devices/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Living Room Sensor",
            "device_type": "sensor",
            "serial_number": "SN-123456",
            "status": "active",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device created successfully"
    assert "id" in data

    mock_users.find_one.assert_awaited_once_with(
        {
            "_id": user_id
        }
    )

    mock_devices.insert_one.assert_awaited_once()


def test_create_device_duplicate_serial_number(
    client,
    mock_device_service_collections,
    user_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": ObjectId(),
        "serial_number": "SN-123456",
    }

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.post(
        "/devices/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Living Room Sensor",
            "device_type": "sensor",
            "serial_number": "SN-123456",
            "status": "active",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["message"] == "Serial number already exists"

    mock_devices.insert_one.assert_not_awaited()

def test_create_device_user_not_found(
    client,
    mock_device_service_collections,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = None

    user_id = ObjectId()

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.post(
        "/devices/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Living Room Sensor",
            "device_type": "sensor",
            "serial_number": "SN-123456",
            "status": "active",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "User not found"

    mock_devices.insert_one.assert_not_awaited()


def test_get_devices(
    client,
    mock_device_service_collections,
    user_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    device = {
        "id": str(ObjectId()),
        "name": "Living Room Sensor",
        "device_type": "sensor",
        "serial_number": "SN-123456",
        "status": "active",
        "is_online": False,
        "owner": {
            "id": str(user_id),
            "name": "Test User",
            "phone": "09123456789",
        },
    }

    async def fake_cursor():
        yield device

    mock_cursor = MagicMock()

    mock_cursor.__aiter__.side_effect = fake_cursor

    mock_devices.aggregate.return_value = mock_cursor
    mock_devices.count_documents.return_value = 1

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        "/devices/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == 1

    assert data["items"][0]["name"] == "Living Room Sensor"


def test_get_devices_by_status(
    client,
    mock_device_service_collections,
    user_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    async def fake_cursor():
        yield {
            "id": str(ObjectId()),
            "name": "Living Room Sensor",
            "device_type": "sensor",
            "serial_number": "SN-123456",
            "status": "active",
            "is_online": True,
            "owner": {
                "id": str(user_id),
                "name": "Test User",
                "phone": "09123456789",
            },
        }

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.side_effect = fake_cursor

    mock_devices.aggregate.return_value = mock_cursor
    mock_devices.count_documents.return_value = 1

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        "/devices/?status=active",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "active"


def test_get_device(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "name": "Living Room Sensor",
        "device_type": "sensor",
        "serial_number": "SN-123456",
        "status": "active",
        "is_online": False,
        "owner_id": user_id,
    }

    async def fake_cursor():
        yield {
            "id": str(device_id),
            "name": "Living Room Sensor",
            "device_type": "sensor",
            "serial_number": "SN-123456",
            "status": "active",
            "is_online": False,
            "owner": {
                "id": str(user_id),
                "name": "Test User",
                "phone": "09123456789",
            },
        }

    mock_cursor = MagicMock()
    mock_cursor.__aiter__.side_effect = fake_cursor

    mock_devices.aggregate.return_value = mock_cursor

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(device_id)
    assert data["name"] == "Living Room Sensor"
    assert data["serial_number"] == "SN-123456"


def test_get_device_invalid_id(
    client,
    mock_device_service_collections,
    user_id,
):
    mock_devices, mock_users = mock_device_service_collections

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        "/devices/invalid-id",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"


def test_get_device_not_found(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_devices.find_one.return_value = None

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "Device not found"


def test_get_device_forbidden(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    another_user_id = ObjectId()

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "name": "Another User Device",
        "device_type": "sensor",
        "serial_number": "SN-999999",
        "status": "active",
        "is_online": False,
        "owner_id": another_user_id,
    }

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.get(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["message"] == "You don't have permission to access this device"


def test_update_device(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "name": "Old Name",
        "device_type": "sensor",
        "serial_number": "SN-123456",
        "status": "active",
        "is_online": False,
        "owner_id": user_id,
    }

    mock_devices.update_one.return_value.matched_count = 1

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.put(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "New Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device updated successfully"

    mock_devices.update_one.assert_awaited_once()


def test_update_device_no_fields(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "owner_id": user_id,
        "serial_number": "SN-123456",
    }

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.put(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={},
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "No fields to update"


def test_update_device_forbidden(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    another_user_id = ObjectId()

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "owner_id": another_user_id,
    }

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.put(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Hacked Device",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["message"] == "You don't have permission to update this device"


def test_delete_device(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "owner_id": user_id,
    }

    mock_devices.delete_one.return_value.deleted_count = 1

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device deleted successfully"

    mock_devices.delete_one.assert_awaited_once()


def test_delete_device_not_found(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    mock_devices.find_one.return_value = None

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "Device not found"


def test_delete_device_forbidden(
    client,
    mock_device_service_collections,
    user_id,
    device_id,
):
    mock_devices, mock_users = mock_device_service_collections

    another_user_id = ObjectId()

    mock_users.find_one.return_value = {
        "_id": user_id,
        "name": "Test User",
        "phone": "09123456789",
    }

    mock_devices.find_one.return_value = {
        "_id": device_id,
        "owner_id": another_user_id,
    }

    token = create_access_token(
        {
            "user_id": str(user_id)
        }
    )

    response = client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["message"] == "You don't have permission to delete this device"