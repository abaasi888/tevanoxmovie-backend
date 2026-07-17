from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionCreate(BaseModel):
    plan: str  # 'weekly', 'biweekly', 'monthly'
    payment_method: str
    transaction_id: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    plan: str
    amount: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    days_remaining: Optional[int] = None