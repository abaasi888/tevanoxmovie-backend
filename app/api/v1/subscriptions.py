from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.schemas.subscription_schema import SubscriptionCreate
from app.services.subscription_service import SubscriptionService

router = APIRouter()

SUBSCRIPTION_PLANS = {
    "weekly": {"duration": 7, "price": 7000},
    "biweekly": {"duration": 14, "price": 12000},
    "monthly": {"duration": 30, "price": 20000}
}

@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return [
        {
            "id": "weekly",
            "name": "Weekly",
            "price": 7000,
            "duration": 7,
            "features": ["Unlimited Movies", "Unlimited Music", "Download for Offline"]
        },
        {
            "id": "biweekly",
            "name": "Bi-Weekly",
            "price": 12000,
            "duration": 14,
            "features": ["Unlimited Movies", "Unlimited Music", "Download for Offline", "Ad-free"]
        },
        {
            "id": "monthly",
            "name": "Monthly",
            "price": 20000,
            "duration": 30,
            "features": ["Unlimited Movies", "Unlimited Music", "Download for Offline", "Ad-free", "Exclusive Content"],
            "popular": True
        }
    ]

@router.post("/activate")
async def activate_subscription(
    subscription_data: SubscriptionCreate,
    current_user = Depends(get_current_user)
):
    """Activate a subscription plan"""
    db = get_database()
    
    plan = SUBSCRIPTION_PLANS.get(subscription_data.plan)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Check if user already has active subscription
    existing = await db.subscriptions.find_one({
        "user_id": current_user["_id"],
        "is_active": True,
        "end_date": {"$gt": datetime.utcnow()}
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="User already has an active subscription")
    
    # Create subscription
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan["duration"])
    
    subscription = {
        "user_id": current_user["_id"],
        "plan": subscription_data.plan,
        "amount": plan["price"],
        "start_date": start_date,
        "end_date": end_date,
        "is_active": True,
        "payment_method": subscription_data.payment_method,
        "transaction_id": subscription_data.transaction_id,
        "created_at": datetime.utcnow()
    }
    
    result = await db.subscriptions.insert_one(subscription)
    
    # Update user's active status
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "is_active": True,
                "subscription_expiry": end_date
            }
        }
    )
    
    return {
        "message": "Subscription activated successfully",
        "subscription_id": str(result.inserted_id),
        "plan": subscription_data.plan,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/status")
async def get_subscription_status(
    current_user = Depends(get_current_user)
):
    """Get current user's subscription status"""
    db = get_database()
    
    subscription = await db.subscriptions.find_one({
        "user_id": current_user["_id"],
        "is_active": True,
        "end_date": {"$gt": datetime.utcnow()}
    })
    
    if not subscription:
        return {
            "is_active": False,
            "message": "No active subscription"
        }
    
    days_remaining = (subscription["end_date"] - datetime.utcnow()).days
    
    return {
        "is_active": True,
        "plan": subscription["plan"],
        "start_date": subscription["start_date"],
        "end_date": subscription["end_date"],
        "days_remaining": max(0, days_remaining),
        "amount": subscription["amount"]
    }

@router.post("/cancel")
async def cancel_subscription(
    current_user = Depends(get_current_user)
):
    """Cancel current subscription"""
    db = get_database()
    
    # Find active subscription
    subscription = await db.subscriptions.find_one({
        "user_id": current_user["_id"],
        "is_active": True,
        "end_date": {"$gt": datetime.utcnow()}
    })
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    # Cancel subscription
    await db.subscriptions.update_one(
        {"_id": subscription["_id"]},
        {"$set": {"is_active": False, "cancelled_at": datetime.utcnow()}}
    )
    
    # Update user's active status
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Subscription cancelled successfully"}

@router.get("/history")
async def get_subscription_history(
    current_user = Depends(get_current_user)
):
    """Get user's subscription history"""
    db = get_database()
    
    subscriptions = await db.subscriptions.find({
        "user_id": current_user["_id"]
    }).sort([("created_at", -1)]).to_list(length=50)
    
    return [
        {
            "id": str(s["_id"]),
            "plan": s["plan"],
            "amount": s["amount"],
            "start_date": s["start_date"],
            "end_date": s["end_date"],
            "is_active": s.get("is_active", False),
            "payment_method": s.get("payment_method"),
            "created_at": s["created_at"]
        }
        for s in subscriptions
    ]