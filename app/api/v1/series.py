from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_series(
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all series with filters"""
    db = get_database()
    
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    series = await db.series.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(s["_id"]),
            "title": s["title"],
            "description": s["description"],
            "category": s["category"],
            "genre": s.get("genre", []),
            "release_year": s["release_year"],
            "seasons": s.get("seasons", 1),
            "episodes": s.get("episodes", 0),
            "poster_url": s.get("poster_url"),
            "cover_url": s.get("cover_url"),
            "vj_name": s.get("vj_name"),
            "total_views": s.get("total_views", 0),
            "created_at": s["created_at"]
        }
        for s in series
    ]

@router.get("/trending")
async def get_trending_series(
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_user)
):
    """Get trending series"""
    db = get_database()
    
    series = await db.series.find({"is_active": True}).sort(
        [("total_views", -1), ("created_at", -1)]
    ).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(s["_id"]),
            "title": s["title"],
            "description": s["description"],
            "category": s["category"],
            "genre": s.get("genre", []),
            "release_year": s["release_year"],
            "seasons": s.get("seasons", 1),
            "episodes": s.get("episodes", 0),
            "poster_url": s.get("poster_url"),
            "cover_url": s.get("cover_url"),
            "vj_name": s.get("vj_name"),
            "total_views": s.get("total_views", 0),
            "created_at": s["created_at"]
        }
        for s in series
    ]

@router.get("/{series_id}")
async def get_series_detail(
    series_id: str,
    current_user = Depends(get_current_user)
):
    """Get series by ID with episodes"""
    db = get_database()
    
    series = await db.series.find_one({"_id": series_id})
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    
    # Get episodes
    episodes = await db.episodes.find({
        "series_id": series_id
    }).sort([("season", 1), ("episode_number", 1)]).to_list(length=100)
    
    return {
        "id": str(series["_id"]),
        "title": series["title"],
        "description": series["description"],
        "category": series["category"],
        "genre": series.get("genre", []),
        "release_year": series["release_year"],
        "seasons": series.get("seasons", 1),
        "episodes": series.get("episodes", 0),
        "poster_url": series.get("poster_url"),
        "cover_url": series.get("cover_url"),
        "vj_id": series.get("vj_id"),
        "vj_name": series.get("vj_name"),
        "total_views": series.get("total_views", 0),
        "created_at": series["created_at"],
        "episodes_list": [
            {
                "id": str(e["_id"]),
                "title": e["title"],
                "episode_number": e["episode_number"],
                "season": e["season"],
                "duration": e.get("duration"),
                "thumbnail_url": e.get("thumbnail_url"),
                "video_url": e.get("video_url"),
                "description": e.get("description"),
                "release_date": e.get("release_date")
            }
            for e in episodes
        ]
    }

@router.get("/{series_id}/episodes")
async def get_episodes(
    series_id: str,
    season: Optional[int] = None,
    current_user = Depends(get_current_user)
):
    """Get episodes of a series"""
    db = get_database()
    
    query = {"series_id": series_id}
    if season:
        query["season"] = season
    
    episodes = await db.episodes.find(query).sort([
        ("season", 1),
        ("episode_number", 1)
    ]).to_list(length=100)
    
    return [
        {
            "id": str(e["_id"]),
            "title": e["title"],
            "episode_number": e["episode_number"],
            "season": e["season"],
            "duration": e.get("duration"),
            "thumbnail_url": e.get("thumbnail_url"),
            "video_url": e.get("video_url"),
            "description": e.get("description"),
            "release_date": e.get("release_date")
        }
        for e in episodes
    ]