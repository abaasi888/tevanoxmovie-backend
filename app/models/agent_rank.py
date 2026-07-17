from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AgentRank(BaseModel):
    id: Optional[str] = None
    name: str  # 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Double Diamond', 'Crown'
    level: int  # 1-7
    min_referrals: int
    max_referrals: int
    commission_rate: float  # 0.25 for 25%
    level_2_rate: float = 0.10
    level_3_rate: float = 0.05
    override_rate: float  # 0-0.15
    one_time_bonus: float
    monthly_bonus: float
    rank_color: str
    rank_icon: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None

class RankRequirements(BaseModel):
    referrals_needed: int
    team_size: Optional[int] = None
    downline_ranks: Optional[int] = None
    years_active: Optional[int] = None