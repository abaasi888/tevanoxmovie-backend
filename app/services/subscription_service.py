from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_database

SUBSCRIPTION_PLANS = {
    "weekly": {"duration": 7, "price": 7000},
    "biweekly": {"duration": 14, "price": 12000},
    "monthly": {"duration": 30, "price": 20000}
}

class SubscriptionService:
    def __init__(self):
        self.db = get_database()
    
    async def activate_subscription(self, user_id: str, plan: str, payment_method: str, transaction_id: Optional[str] = None) -> dict:
        plan_data = SUBSCRIPTION_PLANS.get(plan)
        if not plan_data:
            raise ValueError("Invalid plan")
        
        # Check existing subscription
        existing = await self.db.subscriptions.find_one({
            "user_id": user_id,
            "is_active": True,
            "end_date": {"$gt": datetime.utcnow()}
        })
        
        if existing:
            raise ValueError("User already has an active subscription")
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan_data["duration"])
        
        subscription = {
            "user_id": user_id,
            "plan": plan,
            "amount": plan_data["price"],
            "start_date": start_date,
            "end_date": end_date,
            "is_active": True,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.subscriptions.insert_one(subscription)
        
        # Update user
        await self.db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "is_active": True,
                    "subscription_expiry": end_date
                }
            }
        )
        
        return {
            "subscription_id": str(result.inserted_id),
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date
        }
    
    async def get_active_subscription(self, user_id: str) -> Optional[dict]:
        return await self.db.subscriptions.find_one({
            "user_id": user_id,
            "is_active": True,
            "end_date": {"$gt": datetime.utcnow()}
        })
    
    async def cancel_subscription(self, user_id: str) -> bool:
        result = await self.db.subscriptions.update_one(
            {
                "user_id": user_id,
                "is_active": True,
                "end_date": {"$gt": datetime.utcnow()}
            },
            {
                "$set": {
                    "is_active": False,
                    "cancelled_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count > 0:
            await self.db.users.update_one(
                {"_id": user_id},
                {"$set": {"is_active": False}}
            )
            return True
        return False