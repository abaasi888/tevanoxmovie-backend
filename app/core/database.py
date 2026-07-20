from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB Atlas with SSL disabled for Render compatibility"""
    try:
        # Check if it's an Atlas connection (contains 'mongodb.net' or 'mongodb+srv')
        is_atlas = 'mongodb.net' in settings.MONGO_URI or 'mongodb+srv' in settings.MONGO_URI
        
        if is_atlas:
            logger.info("🔒 Connecting to MongoDB Atlas...")
            
            # Create client with SSL disabled (tlsAllowInvalidCertificates bypasses SSL verification)
            db.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                w='majority',
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=45000,
            )
            logger.info("🔒 SSL verification disabled for Render compatibility")
        else:
            # For localhost, no SSL needed
            logger.info("🔓 Connecting to local MongoDB...")
            db.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
            )
        
        db.db = db.client[settings.MONGO_DB_NAME]
        
        # Test connection with a ping
        await db.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
        
        # Create indexes (with error handling)
        try:
            # Users collection indexes
            await db.db.users.create_index("email", unique=True)
            await db.db.users.create_index("username", unique=True)
            await db.db.users.create_index("referral_code", unique=True)
            
            # Agents collection indexes
            await db.db.agents.create_index("email", unique=True)
            await db.db.agents.create_index("agent_code", unique=True)
            
            # Movies collection indexes
            await db.db.movies.create_index("title")
            await db.db.movies.create_index("category")
            await db.db.movies.create_index("genre")
            
            # Shareholders collection indexes
            await db.db.shareholders.create_index("user_id")
            await db.db.shareholders.create_index("email")
            
            # Dividends collection indexes
            await db.db.dividends.create_index("shareholder_id")
            await db.db.dividends.create_index("status")
            
            logger.info("✅ All indexes created/verified")
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")
        
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