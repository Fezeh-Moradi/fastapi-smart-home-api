from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import pytest

@pytest.mark.asyncio
async def test_mongodb_connection():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    database = client[settings.TEST_DATABASE_NAME]
    result = await database.command("ping")

    assert result["ok"] == 1
    client.close()