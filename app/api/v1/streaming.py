from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from app.services.streaming_service import HomeServerStreamingService
from app.core.database import get_database
from app.api.v1.auth import oauth2_scheme
from jose import JWTError, jwt
from app.core.config import settings

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

@router.get("/movie/{movie_id}")
async def get_movie_stream(
    movie_id: str,
    current_user = Depends(get_current_user),
    streaming_service: HomeServerStreamingService = Depends()
):
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=403, detail="Active subscription required")
    
    db = get_database()
    movie = await db.movies.find_one({"_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    urls = streaming_service.get_streaming_url(movie.get("file_path", ""))
    
    await db.movies.update_one(
        {"_id": movie_id},
        {"$inc": {"total_views": 1}}
    )
    
    return {
        "id": str(movie["_id"]),
        "title": movie["title"],
        "duration": movie.get("duration", 0),
        "streaming": urls,
        "expires_in": 3600,
        "download_url": streaming_service.generate_presigned_download_url(movie.get("file_path", ""))
    }

@router.get("/download/{content_id}")
async def get_download_url(
    content_id: str,
    content_type: str = Query(..., regex="^(movie|series|music)$"),
    current_user = Depends(get_current_user),
    streaming_service: HomeServerStreamingService = Depends()
):
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=403, detail="Active subscription required")
    
    db = get_database()
    
    if content_type == "movie":
        content = await db.movies.find_one({"_id": content_id})
    elif content_type == "series":
        content = await db.episodes.find_one({"_id": content_id})
    else:
        content = await db.music.find_one({"_id": content_id})
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    url = streaming_service.generate_presigned_download_url(content.get("file_path", ""))
    if not url:
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
    
    return {
        "download_url": url,
        "filename": content["title"],
        "expires_in": 3600
    }