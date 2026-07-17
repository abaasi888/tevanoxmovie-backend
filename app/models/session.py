from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

class Session(BaseModel):
    id: Optional[str] = None
    user_id: str
    token: str
    device_type: str  # 'web', 'mobile', 'agent'
    device_name: str
    device_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    expires_at: datetime = datetime.utcnow() + timedelta(days=30)
    last_activity: datetime = datetime.utcnow()
    ended_at: Optional[datetime] = None
    end_reason: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}