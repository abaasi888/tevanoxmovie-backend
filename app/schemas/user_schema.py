from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    agent_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    referral_code: str
    is_active: bool
    is_admin: bool = False
    full_name: Optional[str] = None
    phone: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user: UserResponse
