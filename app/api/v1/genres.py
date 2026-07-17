from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.genre import Genre, GenreCreate, GenreUpdate

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/genres")
async def get_all_genres(
    type: Optional[str] = Query(None, regex="^(movie|series|music)$"),
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    query = {}
    if type:
        query["type"] = type
    if is_active is not None:
        query["is_active"] = is_active
    
    genres = await db.genres.find(query).sort("display_order", 1).to_list(length=100)
    
    return [
        {
            "id": str(g["_id"]),
            "name": g["name"],
            "slug": g["slug"],
            "type": g["type"],
            "icon": g.get("icon"),
            "color": g.get("color"),
            "description": g.get("description"),
            "is_active": g.get("is_active", True),
            "display_order": g.get("display_order", 0),
            "is_deletable": g.get("is_deletable", True),
            "created_at": g["created_at"]
        }
        for g in genres
    ]

@router.post("/genres")
async def create_genre(
    genre_data: GenreCreate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    existing = await db.genres.find_one({"slug": genre_data.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Genre with this slug already exists")
    
    genre = {
        "name": genre_data.name,
        "slug": genre_data.slug,
        "type": genre_data.type,
        "icon": genre_data.icon,
        "color": genre_data.color,
        "description": genre_data.description,
        "display_order": genre_data.display_order,
        "is_active": True,
        "is_deletable": True,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.genres.insert_one(genre)
    genre["_id"] = str(result.inserted_id)
    
    return {"message": "Genre created successfully", "genre": genre}

@router.put("/genres/{genre_id}")
async def update_genre(
    genre_id: str,
    genre_data: GenreUpdate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    update_data = {k: v for k, v in genre_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.genres.update_one({"_id": genre_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    return {"message": "Genre updated successfully"}

@router.delete("/genres/{genre_id}")
async def delete_genre(
    genre_id: str,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    movies = await db.movies.find({"genre_ids": genre_id}).to_list(length=1)
    if movies:
        raise HTTPException(status_code=400, detail="Cannot delete genre with associated content")
    
    result = await db.genres.delete_one({"_id": genre_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    return {"message": "Genre deleted successfully"}