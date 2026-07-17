from datetime import datetime
from typing import Dict, List
from app.core.database import get_database
from app.core.config import settings

class CommissionService:
    def __init__(self):
        self.db = get_database()
    
    async def calculate_agent_commission(self, agent_id: str, amount: float) -> Dict:
        """Calculate commission for an agent"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"error": "Agent not found"}
        
        commission_rate = agent.get("commission_rate", 0.15)
        commission = amount * commission_rate
        
        # Get upline chain
        upline_id = agent.get("upline_id")
        level_2_commission = 0
        level_3_commission = 0
        
        if upline_id:
            upline = await self.db.agents.find_one({"_id": upline_id})
            if upline:
                level_2_commission = amount * 0.10
                
                upline2_id = upline.get("upline_id")
                if upline2_id:
                    level_3_commission = amount * 0.05
        
        return {
            "agent_id": agent_id,
            "direct_commission": commission,
            "level_2_commission": level_2_commission,
            "level_3_commission": level_3_commission,
            "total_commission": commission + level_2_commission + level_3_commission,
            "rates": {
                "level_1": agent.get("commission_rate", 0.15) * 100,
                "level_2": 10,
                "level_3": 5
            }
        }
    
    async def process_subscription_commission(self, user_id: str, amount: float) -> Dict:
        """Process commission for a subscription"""
        user = await self.db.users.find_one({"_id": user_id})
        if not user:
            return {"error": "User not found"}
        
        agent_id = user.get("agent_id")
        if not agent_id:
            return {"message": "No agent for this user"}
        
        commission_data = await self.calculate_agent_commission(agent_id, amount)
        
        # Pay commissions
        paid_total = 0
        for level in ["direct_commission", "level_2_commission", "level_3_commission"]:
            if level in commission_data and commission_data[level] > 0:
                # Determine which agent to pay
                if level == "direct_commission":
                    target_agent_id = agent_id
                elif level == "level_2_commission":
                    agent = await self.db.agents.find_one({"_id": agent_id})
                    target_agent_id = agent.get("upline_id") if agent else None
                else:
                    agent = await self.db.agents.find_one({"_id": agent_id})
                    if agent and agent.get("upline_id"):
                        upline = await self.db.agents.find_one({"_id": agent["upline_id"]})
                        target_agent_id = upline.get("upline_id") if upline else None
                    else:
                        target_agent_id = None
                
                if target_agent_id:
                    await self.db.agents.update_one(
                        {"_id": target_agent_id},
                        {
                            "$inc": {
                                "wallet_balance": commission_data[level],
                                "total_earnings": commission_data[level]
                            }
                        }
                    )
                    paid_total += commission_data[level]
        
        # Record commission transaction
        await self.db.agent_commissions.insert_one({
            "agent_id": agent_id,
            "user_id": user_id,
            "subscription_amount": amount,
            "commission_amount": paid_total,
            "commission_breakdown": commission_data,
            "month": datetime.utcnow().strftime("%Y-%m"),
            "created_at": datetime.utcnow(),
            "status": "paid"
        })
        
        return {
            "agent_id": agent_id,
            "total_paid": paid_total,
            "commission_data": commission_data
        }
    
    async def update_agent_tier(self, agent_id: str) -> None:
        """Update agent tier based on referral count"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return
        
        referrals = await self.db.users.count_documents({"agent_id": agent_id})
        
        if referrals >= 1000:
            tier = 4
            rate = 0.08
            bonus = 200000
        elif referrals >= 501:
            tier = 3
            rate = 0.10
            bonus = 100000
        elif referrals >= 101:
            tier = 2
            rate = 0.12
            bonus = 50000
        else:
            tier = 1
            rate = 0.15
            bonus = 0
        
        await self.db.agents.update_one(
            {"_id": agent_id},
            {
                "$set": {
                    "tier": tier,
                    "commission_rate": rate,
                    "tier_bonus": bonus,
                    "active_referrals": referrals
                }
            }
        )