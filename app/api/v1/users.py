from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import oauth2_scheme
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.schemas.user_schema import UserUpdate, UserResponse

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db = get_database()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "referral_code": current_user.get("referral_code"),
        "is_active": current_user.get("is_active", False),
        "wallet_balance": current_user.get("wallet_balance", 0),
        "total_earnings": current_user.get("total_earnings", 0),
        "subscription_expiry": current_user.get("subscription_expiry"),
        "created_at": current_user.get("created_at")
    }

@router.put("/profile")
async def update_profile(
    user_data: UserUpdate,
    current_user = Depends(get_current_user)
):
    """Update current user profile"""
    db = get_database()
    
    update_data = {}
    if user_data.username:
        update_data["username"] = user_data.username
    if user_data.profile_pic:
        update_data["profile_pic"] = user_data.profile_pic
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one({"_id": current_user["_id"]})
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(updated_user["_id"]),
            "username": updated_user["username"],
            "email": updated_user["email"],
            "profile_pic": updated_user.get("profile_pic")
        }
    }

@router.get("/history")
async def get_watch_history(current_user = Depends(get_current_user)):
    """Get user's watch history"""
    db = get_database()
    history = await db.watch_history.find({
        "user_id": current_user["_id"]
    }).sort("watched_at", -1).limit(50).to_list(length=50)
    
    return [
        {
            "id": str(h["_id"]),
            "content_id": str(h["content_id"]),
            "content_type": h["content_type"],
            "title": h.get("title"),
            "progress": h.get("progress", 0),
            "watched_at": h["watched_at"]
        }
        for h in history
    ]

@router.get("/favorites")
async def get_favorites(current_user = Depends(get_current_user)):
    """Get user's favorites"""
    db = get_database()
    favorites = await db.favorites.find({
        "user_id": current_user["_id"]
    }).to_list(length=100)
    
    return [
        {
            "id": str(f["_id"]),
            "content_id": str(f["content_id"]),
            "content_type": f["content_type"],
            "title": f.get("title"),
            "added_at": f["added_at"]
        }
        for f in favorites
    ]

@router.post("/favorites/{content_id}")
async def add_favorite(
    content_id: str,
    content_type: str,
    current_user = Depends(get_current_user)
):
    """Add content to favorites"""
    db = get_database()
    
    existing = await db.favorites.find_one({
        "user_id": current_user["_id"],
        "content_id": content_id
    })
    
    if existing:
        return {"message": "Already in favorites"}
    
    await db.favorites.insert_one({
        "user_id": current_user["_id"],
        "content_id": content_id,
        "content_type": content_type,
        "added_at": datetime.utcnow()
    })
    
    return {"message": "Added to favorites"}

@router.delete("/favorites/{content_id}")
async def remove_favorite(
    content_id: str,
    current_user = Depends(get_current_user)
):
    """Remove content from favorites"""
    db = get_database()
    
    await db.favorites.delete_one({
        "user_id": current_user["_id"],
        "content_id": content_id
    })
    
    return {"message": "Removed from favorites"}