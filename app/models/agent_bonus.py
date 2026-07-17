from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AgentBonus(BaseModel):
    id: Optional[str] = None
    agent_id: str
    bonus_type: str  # 'achievement', 'monthly', 'performance'
    rank_level: int
    amount: float
    month: Optional[str] = None  # YYYY-MM for monthly bonuses
    status: str  # 'pending', 'paid'
    paid_date: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None