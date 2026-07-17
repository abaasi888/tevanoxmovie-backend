from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.musician import Musician, MusicianCreate, MusicianUpdate

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/musicians")
async def get_all_musicians(
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    query = {}
    if country:
        query["country"] = country
    if is_active is not None:
        query["is_active"] = is_active
    
    musicians = await db.musicians.find(query).sort("name", 1).to_list(length=100)
    
    return [
        {
            "id": str(m["_id"]),
            "name": m["name"],
            "real_name": m.get("real_name"),
            "country": m.get("country"),
            "genre_ids": m.get("genre_ids", []),
            "description": m.get("description"),
            "is_active": m.get("is_active", True),
            "is_deletable": m.get("is_deletable", True),
            "created_at": m["created_at"]
        }
        for m in musicians
    ]

@router.post("/musicians")
async def create_musician(
    musician_data: MusicianCreate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    existing = await db.musicians.find_one({"name": musician_data.name})
    if existing:
        raise HTTPException(status_code=400, detail="Musician with this name already exists")
    
    musician = {
        "name": musician_data.name,
        "real_name": musician_data.real_name,
        "country": musician_data.country,
        "genre_ids": musician_data.genre_ids,
        "description": musician_data.description,
        "is_active": True,
        "is_deletable": True,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.musicians.insert_one(musician)
    musician["_id"] = str(result.inserted_id)
    
    return {"message": "Musician created successfully", "musician": musician}

@router.put("/musicians/{musician_id}")
async def update_musician(
    musician_id: str,
    musician_data: MusicianUpdate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    update_data = {k: v for k, v in musician_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.musicians.update_one({"_id": musician_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Musician not found")
    
    return {"message": "Musician updated successfully"}

@router.delete("/musicians/{musician_id}")
async def delete_musician(
    musician_id: str,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    music = await db.music.find({"musician_id": musician_id}).to_list(length=1)
    if music:
        raise HTTPException(status_code=400, detail="Cannot delete musician with associated content")
    
    result = await db.musicians.delete_one({"_id": musician_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Musician not found")
    
    return {"message": "Musician deleted successfully"}