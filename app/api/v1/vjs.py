from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.vj import VJ, VJCreate, VJUpdate

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/vjs")
async def get_all_vjs(
    language: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    query = {}
    if language:
        query["language"] = language
    if is_active is not None:
        query["is_active"] = is_active
    
    vjs = await db.vjs.find(query).sort("name", 1).to_list(length=100)
    
    return [
        {
            "id": str(v["_id"]),
            "name": v["name"],
            "code": v["code"],
            "language": v["language"],
            "description": v.get("description"),
            "is_active": v.get("is_active", True),
            "is_deletable": v.get("is_deletable", True),
            "created_at": v["created_at"]
        }
        for v in vjs
    ]

@router.post("/vjs")
async def create_vj(
    vj_data: VJCreate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    existing = await db.vjs.find_one({"code": vj_data.code})
    if existing:
        raise HTTPException(status_code=400, detail="VJ with this code already exists")
    
    vj = {
        "name": vj_data.name,
        "code": vj_data.code,
        "language": vj_data.language,
        "description": vj_data.description,
        "is_active": True,
        "is_deletable": True,
        "created_by": current_user["_id"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.vjs.insert_one(vj)
    vj["_id"] = str(result.inserted_id)
    
    return {"message": "VJ created successfully", "vj": vj}

@router.put("/vjs/{vj_id}")
async def update_vj(
    vj_id: str,
    vj_data: VJUpdate,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    update_data = {k: v for k, v in vj_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.vjs.update_one({"_id": vj_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="VJ not found")
    
    return {"message": "VJ updated successfully"}

@router.delete("/vjs/{vj_id}")
async def delete_vj(
    vj_id: str,
    current_user = Depends(require_admin)
):
    db = get_database()
    
    movies = await db.movies.find({"vj_id": vj_id}).to_list(length=1)
    if movies:
        raise HTTPException(status_code=400, detail="Cannot delete VJ with associated content")
    
    result = await db.vjs.delete_one({"_id": vj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="VJ not found")
    
    return {"message": "VJ deleted successfully"}