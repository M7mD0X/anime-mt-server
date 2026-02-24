from motor.motor_asyncio import AsyncIOMotorClient
import os

client = None
db = None

async def connect_db():
    global client, db
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.anime_mt
    print("✅ Connected to MongoDB!")

def get_db():
    return db