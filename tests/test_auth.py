import pytest
from unittest.mock import patch
from core.security import create_access_token, hash_password
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException
from jose import JWTError
from core.deps import get_current_user




def test_register_user(
    client,
    mock_users_collection
):
    mock_users_collection.find_one.return_value = None
    mock_users_collection.insert_one.return_value.inserted_id = "test-user-id"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "phone": "09123456789",
            "password": "123456",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "User registered successfully"
    assert data["id"] == "test-user-id"

    mock_users_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )

    mock_users_collection.insert_one.assert_awaited_once()


def test_register_existing_user(
    client,
    mock_users_collection,
):
    mock_users_collection.find_one.return_value = {
        "_id": "existing-user-id",
        "phone": "09123456789",
    }

    response = client.post(
        "/auth/register",
        json={
            "name":"Test User",
            "phone": "09123456789",
            "password": "123456",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "User already exists"

    mock_users_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )

    mock_users_collection.insert_one.assert_not_awaited()


def test_login_user(
    client,
    mock_users_collection,
):
    mock_users_collection.find_one.return_value = {
        "_id": "existing-user-id",
        "phone": "09123456789",
        "password": hash_password("123456"),
    }

    response = client.post(
        "/auth/login",
        json={
            "phone": "09123456789",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    mock_users_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )


def test_login_user_not_found(
        client,
        mock_users_collection,
):
    mock_users_collection.find_one.return_value = None

    response = client.post(
        "/auth/login",
        json={
            "phone": "09111111111",
            "password": "123456",
        },
    )

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "User not found"

    mock_users_collection.find_one_awaited_once_with(
        {"phone": '09111111111'}
    )


def test_login_wrong_password(
        client,
        mock_users_collection,
):
    mock_users_collection.find_one.return_value = {
        "_id": "existing-user-id",
        "phone": "09123456789",
        "password": "hashed-password",
    }

    with patch(
        "routers.auth.verify_password",
        return_value=False,
    ):
        response = client.post(
            "/auth/login",
            json={
                "phone": "09123456789",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 400
    data = response.json()

    assert data["success"] is False
    assert data["message"] == "Wrong password"


    mock_users_collection.find_one.assert_awaited_once_with(
        {"phone": "09123456789"}
    )


def test_get_me(
        client,
):

    token = create_access_token(
        {
            "user_id": "test-user-id"
        }
    )
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user-id"


def test_get_me_without_token(
        client,
):
    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401


def test_get_me_invalid_token(
        client,
):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["message"] == "Invalid token"


def test_get_current_user_invalid_token():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with patch(
        "core.deps.jwt.decode",
        side_effect=JWTError,
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_get_current_user_without_user_id():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with patch(
        "core.deps.jwt.decode",
        return_value={},
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


    