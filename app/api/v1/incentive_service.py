from datetime import datetime
from typing import Optional, Dict, List
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)

class IncentiveService:
    """Handles agent incentives, bonuses, and recognition"""
    
    def __init__(self):
        self.db = get_database()
    
    async def get_agent_incentives(self, agent_id: str) -> Dict:
        """Get all incentives for an agent"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"error": "Agent not found"}
        
        rank_level = agent.get("current_rank", 1)
        
        # Get available incentives for this rank
        available = await self.db.agent_incentives.find({
            "rank_level": {"$lte": rank_level},
            "is_active": True,
            "delivered": False
        }).to_list(length=50)
        
        # Get delivered incentives
        delivered = await self.db.agent_incentives.find({
            "agent_id": agent_id,
            "delivered": True
        }).to_list(length=50)
        
        return {
            "available": [
                {
                    "id": str(i["_id"]),
                    "name": i["name"],
                    "category": i["category"],
                    "description": i["description"],
                    "value": i["value"],
                    "requirements": i.get("requirements", {})
                }
                for i in available
            ],
            "delivered": [
                {
                    "id": str(i["_id"]),
                    "name": i["name"],
                    "category": i["category"],
                    "description": i["description"],
                    "value": i["value"],
                    "delivered_date": i.get("delivered_date")
                }
                for i in delivered
            ]
        }
    
    async def check_incentive_eligibility(self, agent_id: str, incentive_id: str) -> Dict:
        """Check if agent is eligible for a specific incentive"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"eligible": False, "reason": "Agent not found"}
        
        incentive = await self.db.agent_incentives.find_one({"_id": incentive_id})
        if not incentive:
            return {"eligible": False, "reason": "Incentive not found"}
        
        # Check if already delivered
        if incentive.get("delivered", False):
            return {"eligible": False, "reason": "Incentive already delivered"}
        
        requirements = incentive.get("requirements", {})
        
        # Check referral requirement
        if "referrals" in requirements:
            if agent.get("active_referrals", 0) < requirements["referrals"]:
                return {
                    "eligible": False,
                    "reason": f"Need {requirements['referrals']} referrals (have {agent.get('active_referrals', 0)})"
                }
        
        # Check team size requirement
        if "team_size" in requirements:
            team_size = len(agent.get("downline_ids", []))
            if team_size < requirements["team_size"]:
                return {
                    "eligible": False,
                    "reason": f"Need {requirements['team_size']} team members (have {team_size})"
                }
        
        # Check rank requirement
        if "rank_level" in requirements:
            if agent.get("current_rank", 1) < requirements["rank_level"]:
                return {
                    "eligible": False,
                    "reason": f"Need rank level {requirements['rank_level']} (current: {agent.get('current_rank', 1)})"
                }
        
        return {"eligible": True}
    
    async def deliver_incentive(self, agent_id: str, incentive_id: str) -> Dict:
        """Deliver an incentive to an agent"""
        # Check eligibility
        eligibility = await self.check_incentive_eligibility(agent_id, incentive_id)
        if not eligibility["eligible"]:
            return {"success": False, "reason": eligibility["reason"]}
        
        # Mark incentive as delivered
        await self.db.agent_incentives.update_one(
            {"_id": incentive_id},
            {
                "$set": {
                    "delivered": True,
                    "delivered_date": datetime.utcnow(),
                    "agent_id": agent_id
                }
            }
        )
        
        # Create achievement record
        incentive = await self.db.agent_incentives.find_one({"_id": incentive_id})
        if incentive:
            await self.db.agent_achievements.insert_one({
                "agent_id": agent_id,
                "achievement_type": "incentive_earned",
                "incentive_id": incentive_id,
                "description": f"Earned {incentive['name']} incentive (Value: {incentive['value']} UGX)",
                "achieved_date": datetime.utcnow(),
                "is_celebrated": False
            })
        
        logger.info(f"✅ Incentive {incentive_id} delivered to agent {agent_id}")
        
        return {
            "success": True,
            "message": f"Incentive delivered successfully!"
        }