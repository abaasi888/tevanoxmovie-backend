from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Episode(BaseModel):
    id: Optional[str] = None
    series_id: str
    title: str
    episode_number: int
    season: int
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    video_url: str
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    total_views: int = 0
    is_active: bool = True
    created_at: datetime = datetime.utcnow()

class Series(BaseModel):
    id: Optional[str] = None
    title: str
    original_title: Optional[str] = None
    description: str
    
    # Category (Dynamic)
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    
    # VJ (Dynamic)
    vj_id: Optional[str] = None
    vj_name: Optional[str] = None
    
    # Genres (Dynamic)
    genre_ids: List[str] = []
    genre_names: List[str] = []
    
    # Series Details
    release_year: int
    seasons: int = 1
    episodes_count: int = 0
    language: Optional[str] = None
    country: Optional[str] = None
    
    # Media
    poster_url: Optional[str] = None
    cover_url: Optional[str] = None
    
    # Cast & Crew
    director: Optional[str] = None
    cast: List[str] = []
    
    # Analytics
    total_views: int = 0
    average_rating: float = 0
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None