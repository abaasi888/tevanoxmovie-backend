from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Musician(BaseModel):
    id: Optional[str] = None
    name: str
    real_name: Optional[str] = None
    country: Optional[str] = None
    genre_ids: List[str] = []
    description: Optional[str] = None
    is_active: bool = True
    is_deletable: bool = True
    created_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class MusicianCreate(BaseModel):
    name: str
    real_name: Optional[str] = None
    country: Optional[str] = None
    genre_ids: List[str] = []
    description: Optional[str] = None

class MusicianUpdate(BaseModel):
    name: Optional[str] = None
    real_name: Optional[str] = None
    country: Optional[str] = None
    genre_ids: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None