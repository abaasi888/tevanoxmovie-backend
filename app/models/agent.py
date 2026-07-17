from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Agent(BaseModel):
    id: Optional[str] = None
    user_id: str
    username: str
    email: str
    password: str
    full_name: str
    phone: str
    agent_code: str
    upline_id: Optional[str] = None
    downline_ids: List[str] = []
    
    # Rank System
    current_rank: int = 1  # 1-7 (Bronze to Crown)
    rank_achieved_date: Optional[datetime] = None
    previous_ranks: List[int] = []
    
    # Referral Tracking
    total_referrals: int = 0
    active_referrals: int = 0
    referral_history: List[dict] = []
    
    # Commission Tracking
    commission_rate: float = 0.15
    level_2_rate: float = 0.10
    level_3_rate: float = 0.05
    override_rate: float = 0.0
    
    # Earnings
    wallet_balance: float = 0
    total_earnings: float = 0
    monthly_earnings: float = 0
    override_earnings: float = 0
    bonus_earnings: float = 0
    
    # Incentives
    incentives_received: List[dict] = []
    incentives_pending: List[dict] = []
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    joined_date: datetime = datetime.utcnow()
    last_active: Optional[datetime] = None
    
    # Subscription Requirement
    subscription_required: bool = True
    has_active_subscription: bool = False
    subscription_expiry: Optional[datetime] = None
    
    # Banking
    bank_details: Optional[dict] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}