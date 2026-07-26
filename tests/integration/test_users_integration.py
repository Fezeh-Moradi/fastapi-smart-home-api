import pytest
from bson import ObjectId
from database.test_mongodb import users_test_collection
from core.security import verify_password

@pytest.mark.asyncio
async def test_create_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    response = await client.post(
        "/users/",
        json={
            "name": "Integration User",
            "phone": "09123456789",
            "password": "123456",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "User created"
    assert "id" in data

    user = await test_db.users.find_one(
        {
            "phone": "09123456789"
        }
    )

    assert user is not None
    assert user["name"] == "Integration User"
    assert user["phone"] == "09123456789"

    assert user["password"] != "123456"


@pytest.mark.asyncio
async def test_get_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    user_id = ObjectId()

    await test_db.users.insert_one(
        {
            "_id": user_id,
            "name": "Get Integration User",
            "phone": "09111111111",
            "password": "hashed-password",
        }
    )

    response = await client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user_id)
    assert data["name"] == "Get Integration User"
    assert data["phone"] == "09111111111"


@pytest.mark.asyncio
async def test_get_users_integration(
    client,
    clean_test_database,
    patch_user_database,
):
    await users_test_collection.insert_many(
        [
            {
                "name": "Alice",
                "phone": "09111111111",
                "password": "hashed-password",
            },
            {
                "name": "Bob",
                "phone": "09222222222",
                "password": "hashed-password",
            },
        ]
    )

    response = await client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["skip"] == 0
    assert data["limit"] == 10

    assert len(data["items"]) == 2

    names = [user["name"] for user in data["items"]]

    assert "Alice" in names
    assert "Bob" in names


@pytest.mark.asyncio
async def test_get_users_filter_by_name_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    await test_db.users.insert_many(
        [
            {
                "name": "Alice",
                "phone": "09111111111",
                "password": "hashed-password",
            },
            {
                "name": "Bob",
                "phone": "09222222222",
                "password": "hashed-password",
            },
            {
                "name": "Alicia",
                "phone": "09333333333",
                "password": "hashed-password",
            },
        ]
    )

    response = await client.get(
        "/users/?name=ali"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    names = [
        user["name"]
        for user in data["items"]
    ]

    assert "Alice" in names
    assert "Alicia" in names
    assert "Bob" not in names



@pytest.mark.asyncio
async def test_get_users_filter_by_phone_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    await test_db.users.insert_many(
        [
            {
                "name": "Alice",
                "phone": "09111111111",
                "password": "hashed-password",
            },
            {
                "name": "Bob",
                "phone": "09222222222",
                "password": "hashed-password",
            },
            {
                "name": "Charlie",
                "phone": "09333333333",
                "password": "hashed-password",
            },
        ]
    )

    response = await client.get(
        "/users/?phone=09111111111"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1

    user = data["items"][0]

    assert user["name"] == "Alice"
    assert user["phone"] == "09111111111"



@pytest.mark.asyncio
async def test_update_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    user_id = ObjectId()

    await test_db.users.insert_one(
        {
            "_id": user_id,
            "name": "Old Name",
            "phone": "09111111111",
            "password": "old-hashed-password",
        }
    )

    response = await client.put(
        f"/users/{str(user_id)}",
        json={
            "name": "New Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User updated successfully"

    user = await test_db.users.find_one(
        {
            "_id": user_id
        }
    )

    assert user is not None
    assert user["name"] == "New Name"
    assert user["phone"] == "09111111111"


@pytest.mark.asyncio
async def test_update_user_password_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    user_id = ObjectId()

    await test_db.users.insert_one(
        {
            "_id": user_id,
            "name": "Password User",
            "phone": "09122222222",
            "password": "old-hashed-password",
        }
    )

    response = await client.put(
        f"/users/{str(user_id)}",
        json={
            "password": "new-password",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User updated successfully"

    user = await test_db.users.find_one(
        {
            "_id": user_id
        }
    )

    assert user is not None

    assert user["password"] != "new-password"

    assert verify_password(
        "new-password",
        user["password"],
    ) is True


@pytest.mark.asyncio
async def test_delete_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_user_database,
):
    user_id = ObjectId()

    await test_db.users.insert_one(
        {
            "_id": user_id,
            "name": "Delete Integration User",
            "phone": "09133333333",
            "password": "hashed-password",
        }
    )

    response = await client.delete(
        f"/users/{str(user_id)}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User deleted successfully"

    user = await test_db.users.find_one(
        {
            "_id": user_id
        }
    )

    assert user is None


@pytest.mark.asyncio
async def test_get_user_invalid_id_integration(
    client,
    clean_test_database,
    patch_user_database,
):
    response = await client.get(
        "/users/invalid-id"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"


@pytest.mark.asyncio
async def test_get_user_not_found_integration(
    client,
    clean_test_database,
    patch_user_database,
):
    user_id = ObjectId()

    response = await client.get(
        f"/users/{str(user_id)}"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "User not found"