from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.models.agent_rank import AgentRank, RankRequirements
from app.services.rank_service import RankService
from app.services.incentive_service import IncentiveService

router = APIRouter()

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/ranks")
async def get_all_ranks(
    current_user = Depends(require_admin)
):
    """Get all agent ranks"""
    db = get_database()
    ranks = await db.agent_ranks.find({"is_active": True}).sort("level", 1).to_list(length=10)
    
    return [
        {
            "id": str(r["_id"]),
            "name": r["name"],
            "level": r["level"],
            "min_referrals": r["min_referrals"],
            "max_referrals": r["max_referrals"],
            "commission_rate": r["commission_rate"],
            "level_2_rate": r.get("level_2_rate", 0.10),
            "level_3_rate": r.get("level_3_rate", 0.05),
            "override_rate": r["override_rate"],
            "one_time_bonus": r["one_time_bonus"],
            "monthly_bonus": r["monthly_bonus"],
            "rank_color": r["rank_color"],
            "rank_icon": r["rank_icon"],
            "description": r.get("description"),
            "is_active": r.get("is_active", True)
        }
        for r in ranks
    ]

@router.post("/ranks")
async def create_rank(
    rank_data: dict,
    current_user = Depends(require_admin)
):
    """Create a new rank"""
    db = get_database()
    
    # Check if rank exists
    existing = await db.agent_ranks.find_one({"level": rank_data["level"]})
    if existing:
        raise HTTPException(status_code=400, detail="Rank with this level already exists")
    
    rank = {
        "name": rank_data["name"],
        "level": rank_data["level"],
        "min_referrals": rank_data["min_referrals"],
        "max_referrals": rank_data["max_referrals"],
        "commission_rate": rank_data["commission_rate"],
        "level_2_rate": rank_data.get("level_2_rate", 0.10),
        "level_3_rate": rank_data.get("level_3_rate", 0.05),
        "override_rate": rank_data["override_rate"],
        "one_time_bonus": rank_data["one_time_bonus"],
        "monthly_bonus": rank_data["monthly_bonus"],
        "rank_color": rank_data["rank_color"],
        "rank_icon": rank_data["rank_icon"],
        "description": rank_data.get("description"),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    result = await db.agent_ranks.insert_one(rank)
    rank["_id"] = str(result.inserted_id)
    
    return {"message": "Rank created successfully", "rank": rank}

@router.put("/ranks/{rank_id}")
async def update_rank(
    rank_id: str,
    rank_data: dict,
    current_user = Depends(require_admin)
):
    """Update a rank"""
    db = get_database()
    
    update_data = {k: v for k, v in rank_data.items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.agent_ranks.update_one({"_id": rank_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rank not found")
    
    return {"message": "Rank updated successfully"}

@router.get("/my-rank")
async def get_my_rank(current_user = Depends(get_current_user)):
    """Get current agent's rank details"""
    db = get_database()
    
    agent = await db.agents.find_one({"user_id": current_user["_id"]})
    if not agent:
        raise HTTPException(status_code=403, detail="User is not an agent")
    
    rank_service = RankService()
    rank_info = await rank_service.get_agent_rank_info(str(agent["_id"]))
    
    # Get next rank requirements
    next_rank = await rank_service.get_next_rank(agent.get("current_rank", 1))
    
    return {
        "current_rank": rank_info,
        "next_rank": {
            "level": next_rank["level"] if next_rank else None,
            "name": next_rank["name"] if next_rank else None,
            "referrals_needed": next_rank["min_referrals"] - agent["active_referrals"] if next_rank else 0,
            "total_needed": next_rank["min_referrals"] if next_rank else 0
        } if next_rank else None,
        "progress_percentage": (agent["active_referrals"] / next_rank["min_referrals"]) * 100 if next_rank else 100
    }

@router.get("/rank-progress")
async def get_rank_progress(current_user = Depends(get_current_user)):
    """Get agent's progress to next rank"""
    db = get_database()
    
    agent = await db.agents.find_one({"user_id": current_user["_id"]})
    if not agent:
        raise HTTPException(status_code=403, detail="User is not an agent")
    
    rank_service = RankService()
    progress = await rank_service.get_rank_progress(str(agent["_id"]))
    
    return progress

@router.get("/incentives/my")
async def get_my_incentives(current_user = Depends(get_current_user)):
    """Get current agent's incentives"""
    db = get_database()
    
    agent = await db.agents.find_one({"user_id": current_user["_id"]})
    if not agent:
        raise HTTPException(status_code=403, detail="User is not an agent")
    
    incentive_service = IncentiveService()
    incentives = await incentive_service.get_agent_incentives(str(agent["_id"]))
    
    return incentives

@router.get("/achievements/my")
async def get_my_achievements(current_user = Depends(get_current_user)):
    """Get current agent's achievements"""
    db = get_database()
    
    agent = await db.agents.find_one({"user_id": current_user["_id"]})
    if not agent:
        raise HTTPException(status_code=403, detail="User is not an agent")
    
    achievements = await db.agent_achievements.find({
        "agent_id": agent["_id"]
    }).sort("achieved_date", -1).to_list(length=50)
    
    return [
        {
            "id": str(a["_id"]),
            "type": a["achievement_type"],
            "description": a["description"],
            "achieved_date": a["achieved_date"],
            "is_celebrated": a.get("is_celebrated", False)
        }
        for a in achievements
    ]