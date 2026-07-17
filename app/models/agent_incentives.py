from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AgentIncentive(BaseModel):
    id: Optional[str] = None
    name: str  # 'Vehicle', 'House', 'Travel', 'Recognition'
    rank_level: int  # 1-7
    description: str
    value: float  # In UGX
    category: str  # 'vehicle', 'house', 'travel', 'recognition'
    requirements: dict  # e.g., {'referrals': 500, 'team_size': 50}
    is_active: bool = True
    delivered: bool = False
    delivered_date: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class IncentiveDelivery(BaseModel):
    incentive_id: str
    agent_id: str
    delivered_at: datetime
    delivery_status: str  # 'pending', 'processing', 'delivered'
    delivery_notes: Optional[str] = None