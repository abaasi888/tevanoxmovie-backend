from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_music(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all music with filters"""
    db = get_database()
    
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"artist": {"$regex": search, "$options": "i"}}
        ]
    
    music = await db.music.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "artist": m["artist"],
            "album": m.get("album"),
            "genre": m.get("genre", []),
            "release_year": m.get("release_year"),
            "duration": m.get("duration"),
            "cover_art": m.get("cover_art"),
            "category": m["category"],
            "total_plays": m.get("total_plays", 0),
            "created_at": m["created_at"]
        }
        for m in music
    ]

@router.get("/trending")
async def get_trending_music(
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user)
):
    """Get trending music"""
    db = get_database()
    
    music = await db.music.find({"is_active": True}).sort(
        [("total_plays", -1), ("created_at", -1)]
    ).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "artist": m["artist"],
            "album": m.get("album"),
            "genre": m.get("genre", []),
            "release_year": m.get("release_year"),
            "duration": m.get("duration"),
            "cover_art": m.get("cover_art"),
            "category": m["category"],
            "total_plays": m.get("total_plays", 0),
            "created_at": m["created_at"]
        }
        for m in music
    ]

@router.get("/{music_id}")
async def get_music(
    music_id: str,
    current_user = Depends(get_current_user)
):
    """Get music by ID"""
    db = get_database()
    
    music = await db.music.find_one({"_id": music_id})
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")
    
    # Increment play count
    await db.music.update_one(
        {"_id": music_id},
        {"$inc": {"total_plays": 1}}
    )
    
    return {
        "id": str(music["_id"]),
        "title": music["title"],
        "artist": music["artist"],
        "album": music.get("album"),
        "genre": music.get("genre", []),
        "release_year": music.get("release_year"),
        "duration": music.get("duration"),
        "cover_art": music.get("cover_art"),
        "audio_url": music.get("audio_url"),
        "video_url": music.get("video_url"),
        "lyrics": music.get("lyrics"),
        "category": music["category"],
        "total_plays": music.get("total_plays", 0),
        "created_at": music["created_at"]
    }