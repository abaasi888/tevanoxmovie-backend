from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Subscription(BaseModel):
    id: Optional[str] = None
    user_id: str
    plan: str  # 'weekly', 'biweekly', 'monthly'
    amount: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()