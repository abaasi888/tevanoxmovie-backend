from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    password_hash: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True
