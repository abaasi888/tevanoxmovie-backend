from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import ssl
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB Atlas with SSL workaround"""
    try:
        # Check if it's an Atlas connection (contains 'mongodb+srv' or 'mongodb.net')
        is_atlas = 'mongodb.net' in settings.MONGO_URI or 'mongodb+srv' in settings.MONGO_URI
        
        if is_atlas:
            # For Atlas, use explicit SSL settings
            db.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            logger.info("🔒 Using SSL for MongoDB Atlas connection")
        else:
            # For localhost, no SSL needed
            db.client = AsyncIOMotorClient(settings.MONGO_URI)
            logger.info("🔓 Using local MongoDB connection")
        
        db.db = db.client[settings.MONGO_DB_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
        
        # Create indexes (with error handling)
        try:
            await db.db.users.create_index("email", unique=True)
            await db.db.users.create_index("referral_code", unique=True)
            await db.db.agents.create_index("email", unique=True)
            await db.db.agents.create_index("agent_code", unique=True)
            await db.db.movies.create_index("title")
            await db.db.movies.create_index("category")
            logger.info("✅ Indexes created/verified")
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning (may already exist): {e}")
        
        return db.db
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        raise

async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("✅ Closed MongoDB connection")

def get_database() -> AsyncIOMotorDatabase:
    if db.db is None:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return db.db