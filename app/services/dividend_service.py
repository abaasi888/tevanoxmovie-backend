from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class DividendService:
    """Handles dividend declarations, calculations, and payments"""
    
    def __init__(self):
        self.db = None
        self.share_price = 15000
    
    async def get_db(self):
        """Get database connection"""
        if self.db is None:
            from app.core.database import get_database
            self.db = get_database()
        return self.db
    
    async def declare_dividend(self, data: dict) -> Dict:
        """Declare a dividend for all shareholders"""
        db = await self.get_db()
        
        total_shares_result = await db.shareholders.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$total_shares"}}}
        ]).to_list(length=1)
        
        total_shares = total_shares_result[0]["total"] if total_shares_result else 0
        
        if total_shares == 0:
            return {"error": "No shares found"}
        
        # Calculate dividend per share
        dividend_per_share = data["total_dividend_pool"] / total_shares
        
        # Create dividend declaration
        declaration = {
            "total_dividend_pool": data["total_dividend_pool"],
            "dividend_per_share": dividend_per_share,
            "total_shares": total_shares,
            "declaration_date": datetime.utcnow(),
            "payment_date": data.get("payment_date", datetime.utcnow() + timedelta(days=30)),
            "status": "pending",
            "notes": data.get("notes"),
            "created_at": datetime.utcnow()
        }
        
        result = await db.dividend_declarations.insert_one(declaration)
        declaration_id = str(result.inserted_id)
        
        # Calculate dividends for each shareholder
        shareholders = await db.shareholders.find({"is_active": True}).to_list(length=1000)
        
        for shareholder in shareholders:
            shares = shareholder.get("total_shares", 0)
            if shares == 0:
                continue
            
            gross_amount = shares * dividend_per_share
            tax = gross_amount * 0.15
            net_amount = gross_amount - tax
            
            dividend = {
                "shareholder_id": str(shareholder["_id"]),
                "amount": net_amount,
                "shares_held": shares,
                "dividend_per_share": dividend_per_share,
                "period_start": data.get("period_start", datetime.utcnow() - timedelta(days=30)),
                "period_end": datetime.utcnow(),
                "declaration_date": datetime.utcnow(),
                "payment_date": data.get("payment_date", datetime.utcnow() + timedelta(days=30)),
                "status": "pending",
                "payment_method": shareholder.get("payment_method", "bank_transfer"),
                "tax_deducted": tax,
                "net_amount": net_amount,
                "reinvested": False,
                "created_at": datetime.utcnow()
            }
            
            await db.dividends.insert_one(dividend)
        
        logger.info(f"✅ Dividend declared: {data['total_dividend_pool']} UGX for {total_shares} shares")
        
        return {
            "success": True,
            "message": "Dividend declared successfully",
            "declaration_id": declaration_id,
            "dividend_per_share": dividend_per_share,
            "total_shareholders": len(shareholders)
        }
    
    async def process_dividend_payment(self, dividend_id: str) -> Dict:
        """Process payment for a specific dividend"""
        db = await self.get_db()
        
        dividend = await db.dividends.find_one({"_id": ObjectId(dividend_id)})
        if not dividend:
            return {"error": "Dividend not found"}
        
        if dividend["status"] != "pending":
            return {"error": f"Dividend status is {dividend['status']}"}
        
        # Update dividend status
        await db.dividends.update_one(
            {"_id": ObjectId(dividend_id)},
            {
                "$set": {
                    "status": "paid",
                    "payment_date": datetime.utcnow()
                }
            }
        )
        
        # Update shareholder
        shareholder = await db.shareholders.find_one({"_id": ObjectId(dividend["shareholder_id"])})
        if shareholder:
            await db.shareholders.update_one(
                {"_id": ObjectId(shareholder["_id"])},
                {
                    "$inc": {
                        "total_dividends_earned": dividend["amount"],
                        "total_profit_share": dividend["amount"]
                    },
                    "$set": {
                        "last_dividend_paid": datetime.utcnow()
                    }
                }
            )
        
        return {
            "success": True,
            "message": "Dividend paid successfully",
            "dividend_id": dividend_id,
            "amount": dividend["amount"],
            "shareholder_id": dividend["shareholder_id"]
        }
    
    async def process_dividend_reinvestment(self, dividend_id: str) -> Dict:
        """Reinvest dividend into additional shares"""
        db = await self.get_db()
        
        dividend = await db.dividends.find_one({"_id": ObjectId(dividend_id)})
        if not dividend:
            return {"error": "Dividend not found"}
        
        if dividend["status"] != "paid":
            return {"error": f"Dividend status is {dividend['status']}"}
        
        if dividend.get("reinvested", False):
            return {"error": "Dividend already reinvested"}
        
        # Calculate additional shares
        share_price = self.share_price
        additional_shares = int(dividend["amount"] / share_price)
        
        if additional_shares == 0:
            return {"error": "Dividend amount too small for reinvestment"}
        
        # Update shareholder
        await db.shareholders.update_one(
            {"_id": ObjectId(dividend["shareholder_id"])},
            {
                "$inc": {
                    "total_shares": additional_shares,
                    "portfolio_value": additional_shares * share_price
                },
                "$push": {
                    "shares_purchased": {
                        "date": datetime.utcnow(),
                        "shares": additional_shares,
                        "price": share_price,
                        "total": additional_shares * share_price,
                        "source": "dividend_reinvestment"
                    }
                }
            }
        )
        
        # Update dividend
        await db.dividends.update_one(
            {"_id": ObjectId(dividend_id)},
            {
                "$set": {
                    "reinvested": True,
                    "reinvested_shares": additional_shares,
                    "reinvested_date": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Dividend reinvested successfully",
            "additional_shares": additional_shares,
            "shareholder_id": dividend["shareholder_id"]
        }
