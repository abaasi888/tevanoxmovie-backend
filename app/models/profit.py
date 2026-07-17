from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class PeriodType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class Profit(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    period_start: datetime
    period_end: datetime
    period_type: PeriodType
    
    # Financial Metrics
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    
    # Distribution Breakdown
    reinvested_percent: float = 0.60
    dividends_percent: float = 0.15
    management_bonus_percent: float = 0.10
    reserves_percent: float = 0.10
    taxes_percent: float = 0.05
    
    # Distribution Amounts
    reinvested_amount: float
    dividends_amount: float
    management_bonus: float
    reserves_amount: float
    taxes_amount: float
    
    # Status
    is_distributed: bool = False
    distribution_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True
