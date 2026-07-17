from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Music(BaseModel):
    id: Optional[str] = None
    title: str
    artist: str
    
    # Musician (Dynamic)
    musician_id: Optional[str] = None
    musician_name: Optional[str] = None
    
    # Category (Dynamic)
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    
    # Genres (Dynamic)
    genre_ids: List[str] = []
    genre_names: List[str] = []
    
    # Music Details
    album: Optional[str] = None
    release_year: Optional[int] = None
    duration: Optional[int] = None
    language: Optional[str] = None
    country: Optional[str] = None
    
    # Media
    cover_art: Optional[str] = None
    audio_url: str
    video_url: Optional[str] = None
    lyrics: Optional[str] = None
    
    # Metadata
    producer: Optional[str] = None
    record_label: Optional[str] = None
    
    # Analytics
    total_plays: int = 0
    total_downloads: int = 0
    
    # Status
    is_active: bool = True
    is_featured: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None