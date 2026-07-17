from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class ShareholderService:
    """Handles shareholder management, tracking, and reporting"""
    
    def __init__(self):
        self.db = None  # Will be initialized with actual database connection
        self.share_price = 15000
    
    async def get_db(self):
        """Get database connection"""
        if self.db is None:
            from app.core.database import get_database
            self.db = get_database()
        return self.db
    
    async def create_shareholder(self, data: dict) -> Dict:
        """Create a new shareholder"""
        db = await self.get_db()
        
        shareholder = {
            "user_id": data.get("user_id"),
            "full_name": data["full_name"],
            "email": data["email"],
            "phone": data.get("phone", ""),
            "total_shares": 0,
            "share_price": self.share_price,
            "total_investment": 0,
            "shares_purchased": [],
            "total_dividends_earned": 0,
            "total_profit_share": 0,
            "portfolio_value": 0,
            "roi": 0,
            "is_active": True,
            "is_verified": False,
            "tier": "bronze",
            "joined_date": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        result = await db.shareholders.insert_one(shareholder)
        shareholder["_id"] = str(result.inserted_id)
        
        return shareholder
    
    async def purchase_shares(self, shareholder_id: str, shares: int, price: float, payment_method: str) -> Dict:
        """Process share purchase"""
        db = await self.get_db()
        
        shareholder = await db.shareholders.find_one({"_id": ObjectId(shareholder_id)})
        if not shareholder:
            return {"error": "Shareholder not found"}
        
        total_amount = shares * price
        
        # Update shareholder
        await db.shareholders.update_one(
            {"_id": ObjectId(shareholder_id)},
            {
                "$inc": {
                    "total_shares": shares,
                    "total_investment": total_amount,
                    "portfolio_value": shares * price
                },
                "$push": {
                    "shares_purchased": {
                        "date": datetime.utcnow(),
                        "shares": shares,
                        "price": price,
                        "total": total_amount
                    }
                }
            }
        )
        
        # Update tier based on total shares
        await self._update_shareholder_tier(shareholder_id)
        
        return {
            "success": True,
            "message": "Shares purchased successfully",
            "shares": shares,
            "total_amount": total_amount
        }
    
    async def _update_shareholder_tier(self, shareholder_id: str):
        """Update shareholder tier based on shares held"""
        db = await self.get_db()
        
        shareholder = await db.shareholders.find_one({"_id": ObjectId(shareholder_id)})
        if not shareholder:
            return
        
        shares = shareholder.get("total_shares", 0)
        
        if shares >= 6000:
            tier = "platinum"
        elif shares >= 4000:
            tier = "gold"
        elif shares >= 2000:
            tier = "silver"
        else:
            tier = "bronze"
        
        await db.shareholders.update_one(
            {"_id": ObjectId(shareholder_id)},
            {"$set": {"tier": tier}}
        )
    
    async def get_shareholder_dashboard(self, shareholder_id: str) -> Dict:
        """Get complete shareholder dashboard"""
        db = await self.get_db()
        
        shareholder = await db.shareholders.find_one({"_id": ObjectId(shareholder_id)})
        if not shareholder:
            return {"error": "Shareholder not found"}
        
        # Get dividends history
        dividends = await db.dividends.find({
            "shareholder_id": shareholder_id
        }).sort("payment_date", -1).limit(20).to_list(length=20)
        
        # Get upcoming dividends
        upcoming = await db.dividends.find({
            "shareholder_id": shareholder_id,
            "status": "pending"
        }).to_list(length=10)
        
        # Calculate total dividends
        total_dividends = sum([d["amount"] for d in dividends if d.get("status") == "paid"])
        
        # Calculate ROI
        total_investment = shareholder.get("total_investment", 0)
        current_value = shareholder.get("total_shares", 0) * shareholder.get("current_share_value", 15000)
        roi = ((current_value + total_dividends - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        return {
            "shareholder": {
                "id": str(shareholder["_id"]),
                "full_name": shareholder["full_name"],
                "email": shareholder["email"],
                "total_shares": shareholder.get("total_shares", 0),
                "share_price": shareholder.get("share_price", 15000),
                "total_investment": shareholder.get("total_investment", 0),
                "portfolio_value": shareholder.get("portfolio_value", 0),
                "tier": shareholder.get("tier", "bronze"),
                "roi": roi
            },
            "dividends": {
                "total_earned": total_dividends,
                "pending": len(upcoming),
                "history": [
                    {
                        "id": str(d["_id"]),
                        "amount": d["amount"],
                        "dividend_per_share": d["dividend_per_share"],
                        "payment_date": d["payment_date"],
                        "status": d["status"]
                    }
                    for d in dividends
                ],
                "upcoming": [
                    {
                        "id": str(d["_id"]),
                        "amount": d["amount"],
                        "declaration_date": d["declaration_date"],
                        "payment_date": d["payment_date"]
                    }
                    for d in upcoming
                ]
            },
            "summary": {
                "total_profit_share": shareholder.get("total_profit_share", 0),
                "unrealized_gain": current_value - total_investment,
                "realized_gain": total_dividends,
                "next_dividend_date": upcoming[0]["payment_date"] if upcoming else None
            }
        }
    
    async def calculate_dividend_for_shareholder(self, shareholder_id: str, dividend_per_share: float) -> Dict:
        """Calculate dividend for a specific shareholder"""
        db = await self.get_db()
        
        shareholder = await db.shareholders.find_one({"_id": ObjectId(shareholder_id)})
        if not shareholder:
            return {"error": "Shareholder not found"}
        
        shares = shareholder.get("total_shares", 0)
        gross_dividend = shares * dividend_per_share
        tax = gross_dividend * 0.15  # 15% withholding tax
        net_dividend = gross_dividend - tax
        
        return {
            "shareholder_id": shareholder_id,
            "shares": shares,
            "dividend_per_share": dividend_per_share,
            "gross_dividend": gross_dividend,
            "tax": tax,
            "net_dividend": net_dividend
        }
