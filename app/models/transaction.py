from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    agent_id: Optional[str] = None
    amount: float
    type: str  # 'subscription', 'commission', 'withdrawal', 'deposit'
    status: str  # 'pending', 'completed', 'failed'
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None