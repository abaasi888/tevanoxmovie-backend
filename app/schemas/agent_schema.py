from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AgentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    phone: str
    referral_code: Optional[str] = None

class AgentLogin(BaseModel):
    email: EmailStr
    password: str

class AgentResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    agent_code: str
    tier: int
    wallet_balance: float = 0
    total_earnings: float = 0
    is_active: bool = True
    joined_date: datetime