from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Movie(BaseModel):
    id: Optional[str] = None
    title: str
    original_title: Optional[str] = None
    description: str
    
    # Category (Dynamic - references categories collection)
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    
    # VJ (Dynamic - references vjs collection)
    vj_id: Optional[str] = None
    vj_name: Optional[str] = None
    
    # Genres (Dynamic - references genres collection)
    genre_ids: List[str] = []
    genre_names: List[str] = []
    
    # Music (Dynamic - references musicians collection)
    musician_id: Optional[str] = None
    musician_name: Optional[str] = None
    
    # Movie Details
    release_year: int
    duration: int
    language: Optional[str] = None
    country: Optional[str] = None
    
    # Media
    poster_url: Optional[str] = None
    cover_url: Optional[str] = None
    file_path: str
    trailer_url: Optional[str] = None
    
    # Cast & Crew
    director: Optional[str] = None
    cast: List[str] = []
    producer: Optional[str] = None
    
    # Analytics
    total_views: int = 0
    total_downloads: int = 0
    average_rating: float = 0
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None