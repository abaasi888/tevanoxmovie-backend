from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VJ(BaseModel):
    id: Optional[str] = None
    name: str
    code: str
    language: str  # 'luganda', 'swahili'
    description: Optional[str] = None
    is_active: bool = True
    is_deletable: bool = True
    created_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class VJCreate(BaseModel):
    name: str
    code: str
    language: str
    description: Optional[str] = None

class VJUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None