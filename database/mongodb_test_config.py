from motor.motor_asyncio import AsyncIOMotorClient

from config import settings


test_client = AsyncIOMotorClient(
    settings.MONGO_URL
)

test_database = test_client["smart_home_test"]

users_test_collection = test_database.users
devices_test_collection = test_database.devices
logs_test_collection = test_database.logs