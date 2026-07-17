from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.models.movie import Movie

class MovieService:
    def __init__(self):
        self.db = get_database()
    
    async def get_movies(
        self,
        category: Optional[str] = None,
        genre: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Movie]:
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
        
        movies = await self.db.movies.find(query).skip(skip).limit(limit).to_list(length=limit)
        return movies
    
    async def get_trending(self, limit: int = 10) -> List[Movie]:
        movies = await self.db.movies.find({"is_active": True}).sort(
            [("total_views", -1), ("created_at", -1)]
        ).limit(limit).to_list(length=limit)
        return movies
    
    async def get_by_id(self, movie_id: str) -> Optional[Movie]:
        return await self.db.movies.find_one({"_id": movie_id})
    
    async def create_movie(self, movie_data: dict) -> str:
        movie_data["created_at"] = datetime.utcnow()
        result = await self.db.movies.insert_one(movie_data)
        return str(result.inserted_id)
    
    async def update_movie(self, movie_id: str, update_data: dict) -> bool:
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.movies.update_one(
            {"_id": movie_id},
            {"$set": update_data}
        )
        return result.matched_count > 0
    
    async def increment_views(self, movie_id: str) -> None:
        await self.db.movies.update_one(
            {"_id": movie_id},
            {"$inc": {"total_views": 1}}
        )