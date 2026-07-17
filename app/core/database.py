from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    db.db = db.client[settings.MONGO_DB_NAME]
    
    # Indexes
    await db.db.users.create_index("email", unique=True)
    await db.db.users.create_index("referral_code", unique=True)
    await db.db.agents.create_index("email", unique=True)
    await db.db.agents.create_index("agent_code", unique=True)
    await db.db.movies.create_index("title")
    await db.db.movies.create_index("category")
    
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("✅ Closed MongoDB connection")

def get_database() -> AsyncIOMotorDatabase:
    return db.db