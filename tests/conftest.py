import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_users_collection():
    with patch("routers.auth.users_collection") as mock_collection:
        mock_collection.find_one = AsyncMock()
        mock_collection.insert_one = AsyncMock()

        yield mock_collection


@pytest.fixture
def mock_user_service_collection():
    with patch("services.user_service.users_collection") as mock_collection:
        mock_collection.count_documents = AsyncMock()
        mock_collection.find = MagicMock()
        mock_collection.find_one = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        mock_collection.delete_one = AsyncMock()

        yield mock_collection
