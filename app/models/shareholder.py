from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class ShareholderTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class ShareholderType(str, Enum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"

class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CHEQUE = "cheque"

class SharePurchase(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    shares: int
    price: float
    total: float
    source: Optional[str] = "purchase"
    transaction_id: Optional[str] = None

class BankDetails(BaseModel):
    bank_name: str
    account_name: str
    account_number: str
    branch: str
    swift_code: Optional[str] = None

class MobileMoneyDetails(BaseModel):
    provider: str  # 'mtn', 'airtel', 'other'
    phone_number: str
    account_name: str

class Shareholder(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    full_name: str
    email: str
    phone: str
    address: Optional[str] = None
    
    # Share Details
    total_shares: int = 0
    share_price: float = 15000  # UGX per share
    total_investment: float = 0
    shares_purchased: List[SharePurchase] = []
    
    # Earnings Tracking
    total_dividends_earned: float = 0
    total_profit_share: float = 0
    unrealized_gain: float = 0
    realized_gain: float = 0
    
    # Current Value
    current_share_value: float = 15000
    portfolio_value: float = 0
    roi: float = 0
    
    # Dividend Settings
    dividend_reinvestment: bool = False
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    bank_details: Optional[BankDetails] = None
    mobile_money: Optional[MobileMoneyDetails] = None
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    shareholder_type: ShareholderType = ShareholderType.INDIVIDUAL
    tier: ShareholderTier = ShareholderTier.BRONZE
    
    # Timestamps
    joined_date: datetime = Field(default_factory=datetime.utcnow)
    last_dividend_paid: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Tax Information
    tin: Optional[str] = None
    tax_residency: str = "Uganda"
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True
