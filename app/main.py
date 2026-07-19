from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1 import (
    auth, users, movies, music, series, 
    subscriptions, agents, admin, payments, streaming,
    shareholders, dividends
)
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TevanoxMovie API",
    version="1.0.0",
    description="Movie Streaming Platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS - Allow all origins for now (update for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://abaasi888.github.io",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "https://tevanoxmovie-web.onrender.com",
        "https://tevanoxmovie-admin.onrender.com",
        "https://tevanoxmovie-mobile.onrender.com",
        "https://tevanoxmovie-agent.onrender.com",
        "*"  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    try:
        await connect_to_mongo()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        # Don't crash the app - it will fail gracefully on endpoints

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    logger.info("✅ Database connection closed")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "domain": "tevanox.com"}

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(movies.router, prefix="/api/v1/movies", tags=["Movies"])
app.include_router(music.router, prefix="/api/v1/music", tags=["Music"])
app.include_router(series.router, prefix="/api/v1/series", tags=["Series"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(streaming.router, prefix="/api/v1/streaming", tags=["Streaming"])

# Shareholder Management Routers
app.include_router(shareholders.router, prefix="/api/v1", tags=["Shareholders"])
app.include_router(dividends.router, prefix="/api/v1", tags=["Dividends"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TevanoxMovie API",
        "version": "1.0.0",
        "status": "running"
    }