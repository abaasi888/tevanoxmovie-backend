from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Genre(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    type: str  # 'movie', 'series', 'music'
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    is_deletable: bool = True
    created_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class GenreCreate(BaseModel):
    name: str
    slug: str
    type: str
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0

class GenreUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None