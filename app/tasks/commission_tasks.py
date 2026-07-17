from datetime import datetime, timedelta
from celery import shared_task
from app.core.database import get_database
from app.services.commission_service import CommissionService

@shared_task
def process_monthly_commissions():
    """Process monthly commission payouts for all agents"""
    import asyncio
    asyncio.run(_process_monthly_commissions_async())

async def _process_monthly_commissions_async():
    db = get_database()
    commission_service = CommissionService()
    
    # Get all active agents
    agents = await db.agents.find({"is_active": True}).to_list(length=1000)
    
    for agent in agents:
        # Calculate commission
        referrals = await db.users.count_documents({
            "agent_id": agent["_id"],
            "is_active": True
        })
        
        if referrals == 0:
            continue
        
        # Process commission
        await commission_service.process_subscription_commission(
            agent["_id"],
            referrals * 20000  # Assuming 20,000 UGX per subscription
        )
        
        # Update tier
        await commission_service.update_agent_tier(str(agent["_id"]))
    
    return {"processed": len(agents)}

@shared_task
def check_expired_subscriptions():
    """Check and deactivate expired subscriptions"""
    import asyncio
    asyncio.run(_check_expired_subscriptions_async())

async def _check_expired_subscriptions_async():
    db = get_database()
    
    expired = await db.subscriptions.find({
        "is_active": True,
        "end_date": {"$lt": datetime.utcnow()}
    }).to_list(length=1000)
    
    for subscription in expired:
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": {"is_active": False}}
        )
        
        await db.users.update_one(
            {"_id": subscription["user_id"]},
            {"$set": {"is_active": False}}
        )
    
    return {"deactivated": len(expired)}

@shared_task
def send_agent_weekly_report():
    """Send weekly report to agents"""
    import asyncio
    asyncio.run(_send_agent_weekly_report_async())

async def _send_agent_weekly_report_async():
    db = get_database()
    
    agents = await db.agents.find({"is_active": True}).to_list(length=1000)
    
    for agent in agents:
        # Get weekly earnings
        week_start = datetime.utcnow() - timedelta(days=7)
        earnings = await db.agent_commissions.find({
            "agent_id": agent["_id"],
            "created_at": {"$gte": week_start}
        }).to_list(length=100)
        
        total = sum(e.get("total_paid", 0) for e in earnings)
        
        # Send email (implement email sending)
        pass
    
    return {"sent": len(agents)}