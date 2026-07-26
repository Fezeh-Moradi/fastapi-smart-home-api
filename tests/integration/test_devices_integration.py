import pytest
from bson import ObjectId

@pytest.mark.asyncio
async def test_create_device_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    response = await client.post(
        "/devices/",
        json={
            "name": "My Smart Device",
            "device_type": "sensor",
            "serial_number": "SN-001",
            "status": "active",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device created successfully"
    assert "id" in data

    device = await test_db.devices.find_one(
        {
            "_id": ObjectId(data["id"])
        }
    )

    assert device is not None
    assert device["name"] == "My Smart Device"
    assert device["serial_number"] == "SN-001"
    assert device["owner_id"] == authenticated_user["user"]["_id"]
    assert device["is_online"] is False


@pytest.mark.asyncio
async def test_get_device_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]
    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Get Device Test",
            "device_type": "sensor",
            "serial_number": "SN-GET-001",
            "status": "active",
            "is_online": False,
            "owner_id": user_id,
        }
    )

    response = await client.get(
        f"/devices/{device_id}",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(device_id)
    assert data["name"] == "Get Device Test"
    assert data["device_type"] == "sensor"
    assert data["serial_number"] == "SN-GET-001"
    assert data["status"] == "active"
    assert data["is_online"] is False

    assert data["owner"]["id"] == str(user_id)
    assert data["owner"]["name"] == "Device Test User"
    assert data["owner"]["phone"] == "09111111111"


@pytest.mark.asyncio
async def test_get_devices_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    other_user_id = ObjectId()

    await test_db.users.insert_one(
        {
            "_id": other_user_id,
            "name": "Other User",
            "phone": "09222222222",
            "password": "hashed-password",
        }
    )

    await test_db.devices.insert_many(
        [
            {
                "name": "My Device 1",
                "device_type": "sensor",
                "serial_number": "SN-LIST-001",
                "status": "active",
                "is_online": False,
                "owner_id": user_id,
            },
            {
                "name": "My Device 2",
                "device_type": "sensor",
                "serial_number": "SN-LIST-002",
                "status": "active",
                "is_online": True,
                "owner_id": user_id,
            },
            {
                "name": "Other User Device",
                "device_type": "sensor",
                "serial_number": "SN-LIST-003",
                "status": "active",
                "is_online": False,
                "owner_id": other_user_id,
            },
        ]
    )

    response = await client.get(
        "/devices/",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == 2

    device_names = {
        device["name"]
        for device in data["items"]
    }

    assert "My Device 1" in device_names
    assert "My Device 2" in device_names
    assert "Other User Device" not in device_names

    for device in data["items"]:
        assert device["owner"]["id"] == str(user_id)
        assert device["owner"]["name"] == "Device Test User"
        assert device["owner"]["phone"] == "09111111111"


@pytest.mark.asyncio
async def test_get_devices_filter_by_status_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    await test_db.devices.insert_many(
        [
            {
                "name": "Active Device",
                "device_type": "sensor",
                "serial_number": "SN-STATUS-001",
                "status": "active",
                "is_online": True,
                "owner_id": user_id,
            },
            {
                "name": "Inactive Device",
                "device_type": "sensor",
                "serial_number": "SN-STATUS-002",
                "status": "inactive",
                "is_online": False,
                "owner_id": user_id,
            },
        ]
    )

    response = await client.get(
        "/devices/?status=active",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    assert data["items"][0]["name"] == "Active Device"
    assert data["items"][0]["status"] == "active"


@pytest.mark.asyncio
async def test_get_devices_filter_by_type_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    await test_db.devices.insert_many(
        [
            {
                "name": "Sensor Device",
                "device_type": "sensor",
                "serial_number": "SN-TYPE-001",
                "status": "active",
                "is_online": True,
                "owner_id": user_id,
            },
            {
                "name": "Camera Device",
                "device_type": "camera",
                "serial_number": "SN-TYPE-002",
                "status": "active",
                "is_online": True,
                "owner_id": user_id,
            },
        ]
    )

    response = await client.get(
        "/devices/?device_type=sensor",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    assert data["items"][0]["name"] == "Sensor Device"
    assert data["items"][0]["device_type"] == "sensor"


@pytest.mark.asyncio
async def test_get_devices_filter_by_online_status_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    await test_db.devices.insert_many(
        [
            {
                "name": "Online Device",
                "device_type": "sensor",
                "serial_number": "SN-ONLINE-001",
                "status": "active",
                "is_online": True,
                "owner_id": user_id,
            },
            {
                "name": "Offline Device",
                "device_type": "sensor",
                "serial_number": "SN-ONLINE-002",
                "status": "active",
                "is_online": False,
                "owner_id": user_id,
            },
        ]
    )

    response = await client.get(
        "/devices/?is_online=true",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    assert data["items"][0]["name"] == "Online Device"
    assert data["items"][0]["is_online"] is True


@pytest.mark.asyncio
async def test_update_device_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]
    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Old Device Name",
            "device_type": "sensor",
            "serial_number": "SN-UPDATE-001",
            "status": "active",
            "is_online": False,
            "owner_id": user_id,
        }
    )

    response = await client.put(
        f"/devices/{device_id}",
        json={
            "name": "Updated Device Name",
            "status": "inactive",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device updated successfully"

    device = await test_db.devices.find_one(
        {
            "_id": device_id
        }
    )

    assert device is not None
    assert device["name"] == "Updated Device Name"
    assert device["status"] == "inactive"

    assert device["device_type"] == "sensor"
    assert device["serial_number"] == "SN-UPDATE-001"
    assert device["owner_id"] == user_id
    assert device["is_online"] is False


@pytest.mark.asyncio
async def test_update_device_serial_number_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]
    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Serial Device",
            "device_type": "sensor",
            "serial_number": "SN-OLD-001",
            "status": "active",
            "is_online": False,
            "owner_id": user_id,
        }
    )

    response = await client.put(
        f"/devices/{device_id}",
        json={
            "serial_number": "SN-NEW-001",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device updated successfully"

    device = await test_db.devices.find_one(
        {
            "_id": device_id
        }
    )

    assert device is not None
    assert device["serial_number"] == "SN-NEW-001"


@pytest.mark.asyncio
async def test_update_device_duplicate_serial_number_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    first_device_id = ObjectId()
    second_device_id = ObjectId()

    await test_db.devices.insert_many(
        [
            {
                "_id": first_device_id,
                "name": "First Device",
                "device_type": "sensor",
                "serial_number": "SN-FIRST-001",
                "status": "active",
                "is_online": False,
                "owner_id": user_id,
            },
            {
                "_id": second_device_id,
                "name": "Second Device",
                "device_type": "sensor",
                "serial_number": "SN-SECOND-001",
                "status": "active",
                "is_online": False,
                "owner_id": user_id,
            },
        ]
    )

    response = await client.put(
        f"/devices/{second_device_id}",
        json={
            "serial_number": "SN-FIRST-001",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["message"] == "Serial number already exists"

    second_device = await test_db.devices.find_one(
        {
            "_id": second_device_id
        }
    )

    assert second_device is not None
    assert second_device["serial_number"] == "SN-SECOND-001"


@pytest.mark.asyncio
async def test_update_device_unauthorized_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    owner_id = authenticated_user["user"]["_id"]

    second_user_response = await client.post(
        "/auth/register",
        json={
            "name": "Second User",
            "phone": "09999999999",
            "password": "123456",
        },
    )

    assert second_user_response.status_code == 200

    second_login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09999999999",
            "password": "123456",
        },
    )

    assert second_login_response.status_code == 200

    second_user_token = second_login_response.json()["access_token"]

    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Owner Device",
            "device_type": "sensor",
            "serial_number": "SN-AUTH-001",
            "status": "active",
            "is_online": False,
            "owner_id": owner_id,
        }
    )

    response = await client.put(
        f"/devices/{device_id}",
        json={
            "name": "Hacked Device Name",
        },
        headers={
            "Authorization": f"Bearer {second_user_token}",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["message"] == (
        "You don't have permission to update this device"
    )

    device = await test_db.devices.find_one(
        {
            "_id": device_id
        }
    )

    assert device is not None
    assert device["name"] == "Owner Device"


@pytest.mark.asyncio
async def test_delete_device_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]
    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Delete Device",
            "device_type": "sensor",
            "serial_number": "SN-DELETE-001",
            "status": "active",
            "is_online": False,
            "owner_id": user_id,
        }
    )

    response = await client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device deleted successfully"

    device = await test_db.devices.find_one(
        {
            "_id": device_id
        }
    )

    assert device is None


@pytest.mark.asyncio
async def test_delete_device_unauthorized_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    owner_id = authenticated_user["user"]["_id"]

    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Second Delete User",
            "phone": "09888888888",
            "password": "123456",
        },
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09888888888",
            "password": "123456",
        },
    )

    assert login_response.status_code == 200

    second_user_token = login_response.json()["access_token"]

    device_id = ObjectId()

    await test_db.devices.insert_one(
        {
            "_id": device_id,
            "name": "Protected Device",
            "device_type": "sensor",
            "serial_number": "SN-DELETE-AUTH-001",
            "status": "active",
            "is_online": False,
            "owner_id": owner_id,
        }
    )

    response = await client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": f"Bearer {second_user_token}",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["message"] == (
        "You don't have permission to delete this device"
    )

    device = await test_db.devices.find_one(
        {
            "_id": device_id
        }
    )

    assert device is not None
    assert device["name"] == "Protected Device"
    assert device["serial_number"] == "SN-DELETE-AUTH-001"


@pytest.mark.asyncio
async def test_delete_device_not_found_integration(
    client,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    device_id = ObjectId()

    response = await client.delete(
        f"/devices/{device_id}",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "Device not found"


@pytest.mark.asyncio
async def test_get_device_invalid_id_integration(
    client,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    response = await client.get(
        "/devices/invalid-device-id",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"


@pytest.mark.asyncio
async def test_update_device_invalid_id_integration(
    client,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    response = await client.put(
        "/devices/invalid-device-id",
        json={
            "name": "Updated Device",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"


@pytest.mark.asyncio
async def test_delete_device_invalid_id_integration(
    client,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    response = await client.delete(
        "/devices/invalid-device-id",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"


@pytest.mark.asyncio
async def test_create_device_duplicate_serial_number_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    await test_db.devices.insert_one(
        {
            "_id": ObjectId(),
            "name": "Existing Device",
            "device_type": "sensor",
            "serial_number": "SN-DUPLICATE-001",
            "status": "active",
            "is_online": False,
            "owner_id": user_id,
        }
    )

    response = await client.post(
        "/devices/",
        json={
            "name": "Duplicate Device",
            "device_type": "sensor",
            "serial_number": "SN-DUPLICATE-001",
            "status": "active",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["message"] == "Serial number already exists"

    count = await test_db.devices.count_documents(
        {
            "serial_number": "SN-DUPLICATE-001"
        }
    )

    assert count == 1

@pytest.mark.asyncio
async def test_create_device_integration(
    client,
    test_db,
    clean_test_database,
    patch_device_database,
    authenticated_user,
):
    user_id = authenticated_user["user"]["_id"]

    response = await client.post(
        "/devices/",
        json={
            "name": "Integration Device",
            "device_type": "sensor",
            "serial_number": "SN-CREATE-001",
            "status": "active",
        },
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Device created successfully"
    assert "id" in data

    device = await test_db.devices.find_one(
        {
            "_id": ObjectId(data["id"])
        }
    )

    assert device is not None

    assert device["name"] == "Integration Device"
    assert device["device_type"] == "sensor"
    assert device["serial_number"] == "SN-CREATE-001"
    assert device["status"] == "active"

    assert device["owner_id"] == user_id
    assert device["is_online"] is False


@pytest.mark.asyncio
async def test_get_devices_unauthorized_integration(
    client,
    clean_test_database,
    patch_device_database,
):
    response = await client.get(
        "/devices/",
    )

    assert response.status_code == 401

    data = response.json()

    assert data["message"] == "Not authenticated"