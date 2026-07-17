from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MovieCreate(BaseModel):
    title: str
    description: str
    category: str
    genre: List[str] = []
    release_year: int
    duration: int
    original_title: Optional[str] = None
    vj_id: Optional[str] = None
    vj_name: Optional[str] = None
    director: Optional[str] = None
    cast: List[str] = []

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    genre: Optional[List[str]] = None
    is_active: Optional[bool] = None

class MovieResponse(BaseModel):
    id: str
    title: str
    original_title: Optional[str] = None
    description: str
    category: str
    genre: List[str] = []
    release_year: int
    duration: int
    poster_url: Optional[str] = None
    cover_url: Optional[str] = None
    file_path: Optional[str] = None
    vj_id: Optional[str] = None
    vj_name: Optional[str] = None
    director: Optional[str] = None
    cast: List[str] = []
    total_views: int = 0
    total_downloads: int = 0
    average_rating: float = 0
    is_active: bool = True
    created_at: datetime