import pytest


@pytest.mark.asyncio
async def test_register_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_auth_database,
):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Integration User",
            "phone": "09123456789",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User registered successfully"

    user = await test_db.users.find_one(
        {
            "phone": "09123456789"
        }
    )

    assert user is not None
    assert user["name"] == "Integration User"
    assert user["password"] != "123456"


@pytest.mark.asyncio
async def test_login_user_integration(
    client,
    test_db,
    clean_test_database,
    patch_auth_database,
):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Login Integration User",
            "phone": "09111111111",
            "password": "123456",
        },
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09111111111",
            "password": "123456",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_get_me_integration(
    client,
    test_db,
    clean_test_database,
    patch_auth_database,
):
    register_response = await client.post(
    "/auth/register",
    json={
        "name": "Me Integration User",
        "phone": "09222222222",
        "password": "123456",
    },
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09222222222",
            "password": "123456",
        },
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    access_token = login_data["access_token"]

    me_response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert me_response.status_code == 200

    data = me_response.json()

    assert "user_id" in data
    assert data["user_id"]


@pytest.mark.asyncio
async def test_login_wrong_password_integration(
    client,
    clean_test_database,
    patch_auth_database,
):
    register_response = await client.post(
    "/auth/register",
    json={
        "name": "Wrong Password User",
        "phone": "09333333333",
        "password": "123456",
    },
    )

    assert register_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={
            "phone": "09333333333",
            "password": "wrong-password",
        },
    )

    assert login_response.status_code == 400

    data = login_response.json()

    assert data["message"] == "Wrong password"