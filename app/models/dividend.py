from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class DividendStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REINVESTED = "reinvested"

class DividendDeclarationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"

class Dividend(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    shareholder_id: str
    amount: float
    shares_held: int
    dividend_per_share: float
    
    # Period
    period_start: datetime
    period_end: datetime
    declaration_date: datetime = Field(default_factory=datetime.utcnow)
    payment_date: Optional[datetime] = None
    
    # Status
    status: DividendStatus = DividendStatus.PENDING
    payment_method: str
    transaction_id: Optional[str] = None
    
    # Tax
    tax_deducted: float = 0
    net_amount: float = 0
    
    # Reinvestment
    reinvested: bool = False
    reinvested_shares: int = 0
    reinvested_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True

class DividendDeclaration(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    total_dividend_pool: float
    dividend_per_share: float
    total_shares: int
    declaration_date: datetime = Field(default_factory=datetime.utcnow)
    payment_date: datetime
    status: DividendDeclarationStatus = DividendDeclarationStatus.PENDING
    approved_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True
