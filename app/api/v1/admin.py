from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.services.movie_service import MovieService
from app.services.storage_service import StorageService

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    """Check if user is admin"""
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/dashboard")
async def get_admin_dashboard(
    current_user = Depends(require_admin)
):
    """Get admin dashboard data"""
    db = get_database()
    
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    total_movies = await db.movies.count_documents({})
    total_agents = await db.agents.count_documents({})
    active_agents = await db.agents.count_documents({"is_active": True})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_movies": total_movies,
        "total_agents": total_agents,
        "active_agents": active_agents
    }

@router.get("/users")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_admin)
):
    """Get all users (admin only)"""
    db = get_database()
    
    users = await db.users.find({}).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(u["_id"]),
            "username": u["username"],
            "email": u["email"],
            "is_active": u.get("is_active", False),
            "is_admin": u.get("is_admin", False),
            "created_at": u["created_at"]
        }
        for u in users
    ]

@router.get("/agents")
async def get_all_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_admin)
):
    """Get all agents (admin only)"""
    db = get_database()
    
    agents = await db.agents.find({}).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(a["_id"]),
            "username": a["username"],
            "email": a["email"],
            "full_name": a["full_name"],
            "agent_code": a["agent_code"],
            "tier": a["tier"],
            "wallet_balance": a.get("wallet_balance", 0),
            "total_earnings": a.get("total_earnings", 0),
            "is_active": a.get("is_active", True),
            "joined_date": a["joined_date"]
        }
        for a in agents
    ]

@router.post("/movies")
async def add_movie_admin(
    title: str,
    description: str,
    category: str,
    genre: str,
    release_year: int,
    duration: int,
    file: UploadFile = File(...),
    poster: Optional[UploadFile] = File(None),
    current_user = Depends(require_admin)
):
    """Add a new movie (admin only)"""
    db = get_database()
    
    # Upload video to storage
    file_path = f"movies/{datetime.utcnow().strftime('%Y/%m/%d')}_{file.filename}"
    storage_service = StorageService()
    video_url = await storage_service.upload_file(file.file, file_path)
    
    # Upload poster if provided
    poster_url = None
    if poster:
        poster_path = f"posters/{datetime.utcnow().strftime('%Y/%m/%d')}_{poster.filename}"
        poster_url = await storage_service.upload_file(poster.file, poster_path)
    
    movie = {
        "title": title,
        "description": description,
        "category": category,
        "genre": [g.strip() for g in genre.split(",")],
        "release_year": release_year,
        "duration": duration,
        "file_path": file_path,
        "poster_url": poster_url,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.movies.insert_one(movie)
    
    return {
        "message": "Movie added successfully",
        "movie_id": str(result.inserted_id)
    }

@router.put("/movies/{movie_id}")
async def update_movie_admin(
    movie_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    """Update a movie (admin only)"""
    db = get_database()
    
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if is_active is not None:
        update_data["is_active"] = is_active
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.movies.update_one(
        {"_id": movie_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {"message": "Movie updated successfully"}

@router.delete("/movies/{movie_id}")
async def delete_movie_admin(
    movie_id: str,
    current_user = Depends(require_admin)
):
    """Delete a movie (admin only)"""
    db = get_database()
    
    result = await db.movies.delete_one({"_id": movie_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {"message": "Movie deleted successfully"}