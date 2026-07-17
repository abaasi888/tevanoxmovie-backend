from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Category(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    type: str  # 'movie', 'series', 'music'
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    is_deletable: bool = True
    created_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class CategoryCreate(BaseModel):
    name: str
    slug: str
    type: str
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None