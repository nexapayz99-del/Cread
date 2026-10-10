from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client.vcbot

users       = db.users
accounts    = db.accounts
channels    = db.channels
plans       = db.plans

async def init_indexes():
    await users.create_index("user_id", unique=True)
    await accounts.create_index([("owner_id", 1), ("phone", 1)], unique=True)
    await channels.create_index("chat_id", unique=True)
