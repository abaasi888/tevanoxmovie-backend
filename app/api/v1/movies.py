from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.movie import Movie
from app.schemas.movie_schema import MovieCreate, MovieUpdate, MovieResponse
from app.services.movie_service import MovieService
from app.services.storage_service import StorageService

router = APIRouter()

@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    category: Optional[str] = None,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all movies with filters"""
    db = get_database()
    
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    
    if genre:
        query["genre"] = {"$in": [genre]}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    movies = await db.movies.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "original_title": m.get("original_title"),
            "description": m["description"],
            "category": m["category"],
            "genre": m.get("genre", []),
            "release_year": m["release_year"],
            "duration": m["duration"],
            "poster_url": m.get("poster_url"),
            "cover_url": m.get("cover_url"),
            "vj_name": m.get("vj_name"),
            "total_views": m.get("total_views", 0),
            "average_rating": m.get("average_rating", 0),
            "created_at": m["created_at"]
        }
        for m in movies
    ]

@router.get("/trending", response_model=List[MovieResponse])
async def get_trending_movies(
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending movies"""
    db = get_database()
    
    movies = await db.movies.find({"is_active": True}).sort(
        [("total_views", -1), ("created_at", -1)]
    ).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "description": m["description"],
            "category": m["category"],
            "genre": m.get("genre", []),
            "release_year": m["release_year"],
            "duration": m["duration"],
            "poster_url": m.get("poster_url"),
            "cover_url": m.get("cover_url"),
            "vj_name": m.get("vj_name"),
            "total_views": m.get("total_views", 0),
            "average_rating": m.get("average_rating", 0),
            "created_at": m["created_at"]
        }
        for m in movies
    ]

@router.get("/latest", response_model=List[MovieResponse])
async def get_latest_movies(
    limit: int = Query(10, ge=1, le=50)
):
    """Get latest movies"""
    db = get_database()
    
    movies = await db.movies.find({"is_active": True}).sort(
        [("created_at", -1)]
    ).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "description": m["description"],
            "category": m["category"],
            "genre": m.get("genre", []),
            "release_year": m["release_year"],
            "duration": m["duration"],
            "poster_url": m.get("poster_url"),
            "cover_url": m.get("cover_url"),
            "vj_name": m.get("vj_name"),
            "total_views": m.get("total_views", 0),
            "created_at": m["created_at"]
        }
        for m in movies
    ]

@router.get("/category/{category}", response_model=List[MovieResponse])
async def get_movies_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get movies by category"""
    db = get_database()
    
    movies = await db.movies.find({
        "category": category,
        "is_active": True
    }).sort([("created_at", -1)]).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "description": m["description"],
            "category": m["category"],
            "genre": m.get("genre", []),
            "release_year": m["release_year"],
            "duration": m["duration"],
            "poster_url": m.get("poster_url"),
            "cover_url": m.get("cover_url"),
            "vj_name": m.get("vj_name"),
            "total_views": m.get("total_views", 0),
            "created_at": m["created_at"]
        }
        for m in movies
    ]

@router.get("/search")
async def search_movies(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """Search movies by title or description"""
    db = get_database()
    
    movies = await db.movies.find({
        "is_active": True,
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"original_title": {"$regex": q, "$options": "i"}}
        ]
    }).limit(limit).to_list(length=limit)
    
    return [
        {
            "id": str(m["_id"]),
            "title": m["title"],
            "description": m["description"],
            "category": m["category"],
            "genre": m.get("genre", []),
            "release_year": m["release_year"],
            "duration": m["duration"],
            "poster_url": m.get("poster_url"),
            "cover_url": m.get("cover_url"),
            "vj_name": m.get("vj_name"),
            "total_views": m.get("total_views", 0),
            "created_at": m["created_at"]
        }
        for m in movies
    ]

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: str,
    current_user = Depends(get_current_user)
):
    """Get movie by ID"""
    db = get_database()
    
    movie = await db.movies.find_one({"_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return {
        "id": str(movie["_id"]),
        "title": movie["title"],
        "original_title": movie.get("original_title"),
        "description": movie["description"],
        "category": movie["category"],
        "genre": movie.get("genre", []),
        "release_year": movie["release_year"],
        "duration": movie["duration"],
        "poster_url": movie.get("poster_url"),
        "cover_url": movie.get("cover_url"),
        "file_path": movie.get("file_path"),
        "vj_id": movie.get("vj_id"),
        "vj_name": movie.get("vj_name"),
        "director": movie.get("director"),
        "cast": movie.get("cast", []),
        "total_views": movie.get("total_views", 0),
        "total_downloads": movie.get("total_downloads", 0),
        "average_rating": movie.get("average_rating", 0),
        "is_active": movie.get("is_active", True),
        "created_at": movie["created_at"]
    }

@router.post("/{movie_id}/rate")
async def rate_movie(
    movie_id: str,
    rating: int = Query(..., ge=1, le=5),
    current_user = Depends(get_current_user)
):
    """Rate a movie"""
    db = get_database()
    
    movie = await db.movies.find_one({"_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Update or insert rating
    await db.ratings.update_one(
        {
            "user_id": current_user["_id"],
            "content_id": movie_id,
            "content_type": "movie"
        },
        {
            "$set": {
                "rating": rating,
                "rated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Calculate new average rating
    ratings = await db.ratings.find({
        "content_id": movie_id,
        "content_type": "movie"
    }).to_list(length=1000)
    
    if ratings:
        avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
        await db.movies.update_one(
            {"_id": movie_id},
            {"$set": {"average_rating": round(avg_rating, 2)}}
        )
    
    return {"message": "Rating submitted successfully"}

@router.post("/{movie_id}/view")
async def track_view(
    movie_id: str,
    current_user = Depends(get_current_user)
):
    """Track a movie view"""
    db = get_database()
    
    movie = await db.movies.find_one({"_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Increment view count
    await db.movies.update_one(
        {"_id": movie_id},
        {"$inc": {"total_views": 1}}
    )
    
    # Add to watch history
    await db.watch_history.insert_one({
        "user_id": current_user["_id"],
        "content_id": movie_id,
        "content_type": "movie",
        "title": movie["title"],
        "watched_at": datetime.utcnow()
    })
    
    return {"message": "View tracked"}