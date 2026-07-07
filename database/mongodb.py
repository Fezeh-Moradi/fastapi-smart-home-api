from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)

database = client.smart_home

users_collection = database.users
devices_collection = database.devices
logs_collection = database.logs




from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)

database = client.smart_home

users_collection = database.users
devices_collection = database.devices
logs_collection = database.logs