from bson import ObjectId
from unittest.mock import AsyncMock, patch, MagicMock

def test_get_users(
        client,
        mock_user_service_collection,
):
    user_1 = {
        "_id": ObjectId(),
        "name": "Ali",
        "phone": "09123456789",
    }

    user_2 = {
        "_id": ObjectId(),
        "name": "Sara",
        "phone": "09987654321",
    }

    mock_user_service_collection.count_documents.return_value = 2

    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    async def fake_cursor():
        yield user_1
        yield user_2

    mock_cursor.__aiter__.side_effect = fake_cursor

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()

    assert  data["total"] == 2
    assert data["skip"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Ali"
    assert data["items"][1]["name"] == "Sara"


def test_get_users_by_name(
client,
mock_user_service_collection,
):
    user = {
    "_id": ObjectId(),
    "name": "Ali",
    "phone": "09123456789",
    }

    mock_user_service_collection.count_documents.return_value = 1

    mock_cursor = mock_user_service_collection.find.return_value

    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    async def fake_cursor():
        yield user

    mock_cursor.__aiter__.side_effect = fake_cursor

    response = client.get(
        "/users/?name=ali"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Ali"

    mock_user_service_collection.count_documents.assert_awaited_once_with(
        {
            "name": {
                "$regex": "ali",
                "$options": "i",
            }
        }
    )

    mock_user_service_collection.find.assert_called_once_with(
        {
            "name": {
                "$regex": "ali",
                "$options": "i",
            }
        }
    )



def test_get_user(
    client,
    mock_user_service_collection
):
    user_id = ObjectId()

    user = {
        "_id": user_id,
        "name": "Ali",
        "phone": "09123456789",
        
    }

    mock_user_service_collection.find_one.return_value = user

    response = client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(user_id)
    assert data["name"] == "Ali"
    assert data["phone"] == "09123456789"

    mock_user_service_collection.find_one.assert_awaited_once_with(
        {"_id": user_id}
    )

def test_get_user_not_found(
    client,
    mock_user_service_collection,
):
    user_id = str(ObjectId())

    mock_user_service_collection.find_one.return_value = None

    response = client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "User not found"

    mock_user_service_collection.find_one.assert_awaited_once_with(
        {"_id": ObjectId(user_id)}
    )


def test_get_user_invalid_id(
    client,
    mock_user_service_collection,
):
    response = client.get(
    "/users/invalid-id"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"

    mock_user_service_collection.find_one.assert_not_awaited()


def test_create_user(
    client,
    mock_user_service_collection,
):
    mock_user_service_collection.find_one.return_value = None

    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId()

    mock_user_service_collection.insert_one.return_value = mock_result

    with patch(
        "services.user_service.hash_password",
        return_value="hashed-password",
    ) as mock_hash_password:

        response = client.post(
            "/users/",
            json={
                "name": "Ali",
                "phone": "09123456789",
                "password": "123456",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "User created"
    assert data["id"] == str(mock_result.inserted_id)

    mock_user_service_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )

    mock_hash_password.assert_called_once_with(
        "123456"
    )

    mock_user_service_collection.insert_one.assert_awaited_once_with(
        {
            "name": "Ali",
            "phone": "09123456789",
            "password": "hashed-password",
        }
    )



def test_create_user_existing_phone(
    client,
    mock_user_service_collection,
):
    mock_user_service_collection.find_one.return_value = {
    "_id": ObjectId(),
    "name": "Ali",
    "phone": "09123456789",
    }

    with patch(
        "services.user_service.hash_password"
    ) as mock_hash_password:

        response = client.post(
            "/users/",
            json={
                "name": "Another User",
                "phone": "09123456789",
                "password": "123456",
            },
        )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Phone already exists"

    mock_user_service_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )

    mock_user_service_collection.insert_one.assert_not_awaited()

    mock_hash_password.assert_not_called()



def test_update_user(
    client,
    mock_user_service_collection,
):
    user_id = ObjectId()

    mock_result = MagicMock()
    mock_result.matched_count = 1

    mock_user_service_collection.update_one.return_value = mock_result

    response = client.put(
        f"/users/{user_id}",
        json={
            "name": "Ali Updated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User updated successfully"

    mock_user_service_collection.update_one.assert_awaited_once_with(
        {"_id": user_id},
        {
            "$set": {
                "name": "Ali Updated",
            }
        }
    )


def test_update_user_password(
    client,
    mock_user_service_collection,
):
    user_id = ObjectId()

    mock_result = MagicMock()
    mock_result.matched_count = 1

    mock_user_service_collection.update_one.return_value = mock_result

    with patch(
        "services.user_service.hash_password",
        return_value="hashed-new-password",
    ) as mock_hash_password:

        response = client.put(
            f"/users/{user_id}",
            json={
                "password": "new-password",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User updated successfully"

    mock_hash_password.assert_called_once_with(
        "new-password"
    )

    mock_user_service_collection.update_one.assert_awaited_once_with(
        {"_id": user_id},
        {
            "$set": {
                "password": "hashed-new-password",
            }
        }
    )



def test_update_user_not_found(
    client,
    mock_user_service_collection,
):
    user_id = ObjectId()

    mock_result = MagicMock()
    mock_result.matched_count = 0

    mock_user_service_collection.update_one.return_value = mock_result

    response = client.put(
        f"/users/{user_id}",
        json={
            "name": "Ali Updated",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "User not found"

    mock_user_service_collection.update_one.assert_awaited_once_with(
        {"_id": user_id},
        {
            "$set": {
                "name": "Ali Updated",
            }
        }
    )


def test_update_user_invalid_id(
    client,
    mock_user_service_collection,
):
    response = client.put(
    "/users/invalid-id",
    json={
    "name": "Ali Updated",
    },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"

    mock_user_service_collection.update_one.assert_not_awaited()


def test_delete_user(
    client,
    mock_user_service_collection,
):
    user_id = ObjectId()

    mock_result = MagicMock()
    mock_result.deleted_count = 1

    mock_user_service_collection.delete_one.return_value = mock_result

    response = client.delete(
        f"/users/{user_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User deleted successfully"

    mock_user_service_collection.delete_one.assert_awaited_once_with(
        {"_id": user_id}
    )



def test_delete_user_not_found(
    client,
    mock_user_service_collection,
):
    user_id = ObjectId()

    mock_result = MagicMock()
    mock_result.deleted_count = 0

    mock_user_service_collection.delete_one.return_value = mock_result

    response = client.delete(
        f"/users/{user_id}"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "User not found"

    mock_user_service_collection.delete_one.assert_awaited_once_with(
        {"_id": user_id}
    )


def test_delete_user_invalid_id(
    client,
    mock_user_service_collection,
):
    response = client.delete(
    "/users/invalid-id"
    )

    assert response.status_code == 400

    data = response.json()

    assert data["message"] == "Invalid ID"

    mock_user_service_collection.delete_one.assert_not_awaited()



def test_get_users_by_phone(
    client,
    mock_user_service_collection,
):
    user = {
        "_id": ObjectId(),
        "name": "Ali",
        "phone": "09123456789",
    }

    mock_user_service_collection.count_documents.return_value = 1

    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    async def fake_cursor():
        yield user

    mock_cursor.__aiter__.side_effect = fake_cursor

    response = client.get(
        "/users/?phone=09123456789"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Ali"
    assert data["items"][0]["phone"] == "09123456789"


def test_get_users_pagination(
    client,
    mock_user_service_collection,
):
    user = {
    "_id": ObjectId(),
    "name": "Ali",
    "phone": "09123456789",
    }

    mock_user_service_collection.count_documents.return_value = 15

    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    async def fake_cursor():
        yield user

    mock_cursor.__aiter__.side_effect = fake_cursor

    response = client.get(
        "/users/?skip=10&limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 15
    assert data["skip"] == 10
    assert data["limit"] == 5
    assert len(data["items"]) == 1

    mock_user_service_collection.find.assert_called_once_with({})

    mock_cursor.sort.assert_called_once_with(
        "name",
        1
    )

    mock_cursor.skip.assert_called_once_with(10)

    mock_cursor.limit.assert_called_once_with(5)




def test_get_users_sort_name(
    client,
    mock_user_service_collection,
): 
    mock_user_service_collection.count_documents.return_value = 0
    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    async def fake_cursor():
        return
        yield
    mock_cursor.__aiter__.side_effect = fake_cursor
    response = client.get(
        "/users/?sort=name"
    ) 
    assert response.status_code == 200
    mock_cursor.sort.assert_called_once_with(
        "name", 1 
    )

def test_get_users_sort_name_descending( 
    client, 
    mock_user_service_collection, 
):
    mock_user_service_collection.count_documents.return_value = 0
    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    async def fake_cursor():
        return
        yield 
    mock_cursor.__aiter__.side_effect = fake_cursor
    response = client.get( 
        "/users/?sort=-name"
    ) 
    assert response.status_code == 200
    mock_cursor.sort.assert_called_once_with( "name", -1 )


def test_get_users_sort_phone(
    client,
    mock_user_service_collection,
):
    mock_user_service_collection.count_documents.return_value = 0
    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    async def fake_cursor():
        return
        yield
    mock_cursor.__aiter__.side_effect = fake_cursor
    response = client.get(
        "/users/?sort=phone" 
    ) 
    assert response.status_code == 200
    mock_cursor.sort.assert_called_once_with( "phone", 1 )


def test_get_users_sort_phone_descending(
    client,
    mock_user_service_collection,
): 
    mock_user_service_collection.count_documents.return_value = 0
    mock_cursor = mock_user_service_collection.find.return_value
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    async def fake_cursor():
        return
        yield
    mock_cursor.__aiter__.side_effect = fake_cursor
    response = client.get(
        "/users/?sort=-phone"
    )
    assert response.status_code == 200
    mock_cursor.sort.assert_called_once_with( "phone", -1 )


