from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)

database = client[settings.DATABASE_NAME]

users_collection = database.users
devices_collection = database.devices
logs_collection = database.logs