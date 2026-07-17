from datetime import datetime
from typing import Optional, Dict, List
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)

class RankService:
    """Handles agent rank calculations, promotions, and tracking"""
    
    def __init__(self):
        self.db = get_database()
    
    async def get_agent_rank_info(self, agent_id: str) -> Dict:
        """Get detailed rank information for an agent"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"error": "Agent not found"}
        
        rank = await self.db.agent_ranks.find_one({"level": agent.get("current_rank", 1)})
        if not rank:
            return {"error": "Rank not found"}
        
        return {
            "level": rank["level"],
            "name": rank["name"],
            "color": rank["rank_color"],
            "icon": rank["rank_icon"],
            "description": rank.get("description"),
            "commission_rate": rank["commission_rate"] * 100,
            "override_rate": rank["override_rate"] * 100,
            "monthly_bonus": rank["monthly_bonus"],
            "achieved_date": agent.get("rank_achieved_date"),
            "referrals_required": rank["min_referrals"],
            "current_referrals": agent.get("active_referrals", 0)
        }
    
    async def get_next_rank(self, current_level: int) -> Optional[Dict]:
        """Get the next rank requirements"""
        next_level = current_level + 1
        rank = await self.db.agent_ranks.find_one({"level": next_level})
        if not rank:
            return None
        
        return {
            "level": rank["level"],
            "name": rank["name"],
            "min_referrals": rank["min_referrals"],
            "max_referrals": rank["max_referrals"],
            "commission_rate": rank["commission_rate"],
            "override_rate": rank["override_rate"],
            "monthly_bonus": rank["monthly_bonus"],
            "one_time_bonus": rank["one_time_bonus"]
        }
    
    async def get_rank_progress(self, agent_id: str) -> Dict:
        """Get agent's progress to next rank"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"error": "Agent not found"}
        
        current_level = agent.get("current_rank", 1)
        next_rank = await self.get_next_rank(current_level)
        
        if not next_rank:
            return {
                "current_rank": current_level,
                "is_max_rank": True,
                "progress": 100
            }
        
        current_referrals = agent.get("active_referrals", 0)
        needed = next_rank["min_referrals"]
        progress = min((current_referrals / needed) * 100, 100)
        
        return {
            "current_rank": current_level,
            "next_rank": next_rank["level"],
            "next_rank_name": next_rank["name"],
            "referrals_needed": max(0, needed - current_referrals),
            "total_needed": needed,
            "current_referrals": current_referrals,
            "progress_percentage": progress,
            "is_max_rank": False,
            "next_rank_bonus": next_rank["one_time_bonus"],
            "next_commission_rate": next_rank["commission_rate"] * 100
        }
    
    async def check_rank_promotion(self, agent_id: str) -> Dict:
        """Check if agent qualifies for rank promotion"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return {"error": "Agent not found"}
        
        current_level = agent.get("current_rank", 1)
        next_rank = await self.get_next_rank(current_level)
        
        if not next_rank:
            return {"promoted": False, "message": "Already at highest rank"}
        
        active_referrals = agent.get("active_referrals", 0)
        
        if active_referrals >= next_rank["min_referrals"]:
            # Promote agent
            await self.promote_agent(agent_id, next_rank["level"])
            return {
                "promoted": True,
                "new_rank": next_rank["level"],
                "new_rank_name": next_rank["name"],
                "one_time_bonus": next_rank["one_time_bonus"],
                "message": f"Congratulations! You've been promoted to {next_rank['name']}!"
            }
        
        return {
            "promoted": False,
            "current_rank": current_level,
            "needed": next_rank["min_referrals"] - active_referrals,
            "message": f"Need {next_rank['min_referrals'] - active_referrals} more referrals for {next_rank['name']}"
        }
    
    async def promote_agent(self, agent_id: str, new_level: int):
        """Promote an agent to a new rank"""
        agent = await self.db.agents.find_one({"_id": agent_id})
        if not agent:
            return
        
        old_level = agent.get("current_rank", 1)
        
        # Update agent rank
        await self.db.agents.update_one(
            {"_id": agent_id},
            {
                "$set": {
                    "current_rank": new_level,
                    "rank_achieved_date": datetime.utcnow()
                },
                "$push": {
                    "previous_ranks": old_level
                }
            }
        )
        
        # Get rank details for bonus
        rank = await self.db.agent_ranks.find_one({"level": new_level})
        if rank:
            # Create achievement record
            await self.db.agent_achievements.insert_one({
                "agent_id": agent_id,
                "achievement_type": "rank_reached",
                "rank_level": new_level,
                "description": f"Reached {rank['name']} rank",
                "achieved_date": datetime.utcnow(),
                "is_celebrated": False
            })
            
            # Add one-time bonus to wallet
            if rank.get("one_time_bonus", 0) > 0:
                await self.db.agents.update_one(
                    {"_id": agent_id},
                    {
                        "$inc": {
                            "wallet_balance": rank["one_time_bonus"],
                            "bonus_earnings": rank["one_time_bonus"],
                            "total_earnings": rank["one_time_bonus"]
                        }
                    }
                )
                
                # Record bonus
                await self.db.agent_bonuses.insert_one({
                    "agent_id": agent_id,
                    "bonus_type": "achievement",
                    "rank_level": new_level,
                    "amount": rank["one_time_bonus"],
                    "status": "paid",
                    "paid_date": datetime.utcnow(),
                    "created_at": datetime.utcnow()
                })
        
        logger.info(f"✅ Agent {agent_id} promoted from level {old_level} to level {new_level}")
    
    async def calculate_monthly_bonuses(self):
        """Calculate and distribute monthly bonuses"""
        agents = await self.db.agents.find({"is_active": True}).to_list(length=1000)
        
        for agent in agents:
            rank = await self.db.agent_ranks.find_one({"level": agent.get("current_rank", 1)})
            if not rank:
                continue
            
            monthly_bonus = rank.get("monthly_bonus", 0)
            if monthly_bonus > 0:
                # Check if agent met performance criteria
                active_referrals = agent.get("active_referrals", 0)
                min_referrals = rank.get("min_referrals", 0)
                
                # Only pay bonus if they met minimum referrals
                if active_referrals >= min_referrals * 0.5:  # 50% of requirement
                    await self.db.agents.update_one(
                        {"_id": agent["_id"]},
                        {
                            "$inc": {
                                "wallet_balance": monthly_bonus,
                                "bonus_earnings": monthly_bonus,
                                "total_earnings": monthly_bonus
                            }
                        }
                    )
                    
                    # Record bonus
                    await self.db.agent_bonuses.insert_one({
                        "agent_id": agent["_id"],
                        "bonus_type": "monthly",
                        "rank_level": rank["level"],
                        "amount": monthly_bonus,
                        "month": datetime.utcnow().strftime("%Y-%m"),
                        "status": "paid",
                        "paid_date": datetime.utcnow(),
                        "created_at": datetime.utcnow()
                    })
        
        return {"processed": len(agents)}