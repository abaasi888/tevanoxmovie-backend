from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AgentAchievement(BaseModel):
    id: Optional[str] = None
    agent_id: str
    achievement_type: str  # 'rank_reached', 'incentive_earned', 'milestone'
    rank_level: Optional[int] = None
    incentive_id: Optional[str] = None
    description: str
    achieved_date: datetime = datetime.utcnow()
    is_celebrated: bool = False
    celebration_date: Optional[datetime] = None