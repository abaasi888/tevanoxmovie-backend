from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.schemas.agent_schema import AgentCreate, AgentLogin, AgentResponse
from app.services.agent_service import AgentService
from app.services.commission_service import CommissionService
from app.core.security import get_password_hash, verify_password, create_access_token
import uuid

router = APIRouter()

@router.post("/register")
async def register_agent(agent_data: AgentCreate):
    """Register a new sales agent"""
    db = get_database()
    
    # Check if email exists
    existing = await db.agents.find_one({"email": agent_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    existing = await db.users.find_one({"username": agent_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Generate agent code
    agent_code = f"TVX-{uuid.uuid4().hex[:6].upper()}"
    
    # Check if upline exists
    upline_id = None
    if agent_data.referral_code:
        upline = await db.agents.find_one({"agent_code": agent_data.referral_code})
        if upline:
            upline_id = upline["_id"]
    
    # Create agent
    hashed_password = get_password_hash(agent_data.password)
    agent = {
        "username": agent_data.username,
        "email": agent_data.email,
        "password": hashed_password,
        "full_name": agent_data.full_name,
        "phone": agent_data.phone,
        "agent_code": agent_code,
        "upline_id": upline_id,
        "total_referrals": 0,
        "active_referrals": 0,
        "tier": 1,
        "commission_rate": 0.15,
        "wallet_balance": 0,
        "total_earnings": 0,
        "is_active": True,
        "joined_date": datetime.utcnow(),
        "is_salary_eligible": False
    }
    
    result = await db.agents.insert_one(agent)
    agent["_id"] = str(result.inserted_id)
    
    # Create token
    token = create_access_token({"sub": str(result.inserted_id), "type": "agent"})
    
    return {
        "token": token,
        "agent": {
            "id": str(result.inserted_id),
            "username": agent["username"],
            "email": agent["email"],
            "full_name": agent["full_name"],
            "agent_code": agent["agent_code"],
            "tier": agent["tier"],
            "is_active": agent["is_active"]
        }
    }

@router.post("/login")
async def login_agent(agent_data: AgentLogin):
    """Login sales agent"""
    db = get_database()
    
    agent = await db.agents.find_one({"email": agent_data.email})
    if not agent:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not verify_password(agent_data.password, agent["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not agent.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    token = create_access_token({"sub": str(agent["_id"]), "type": "agent"})
    
    return {
        "token": token,
        "agent": {
            "id": str(agent["_id"]),
            "username": agent["username"],
            "email": agent["email"],
            "full_name": agent["full_name"],
            "agent_code": agent["agent_code"],
            "tier": agent["tier"],
            "wallet_balance": agent.get("wallet_balance", 0),
            "total_earnings": agent.get("total_earnings", 0),
            "is_active": agent.get("is_active", True)
        }
    }

@router.get("/dashboard")
async def get_agent_dashboard(
    current_agent = Depends(get_current_user)
):
    """Get agent dashboard data"""
    db = get_database()
    
    agent = await db.agents.find_one({"_id": current_agent["_id"]})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get referrals
    referrals = await db.users.find({
        "agent_id": agent["_id"],
        "is_active": True
    }).to_list(length=100)
    
    active_referrals = len(referrals)
    total_referrals = await db.users.count_documents({"agent_id": agent["_id"]})
    
    # Get earnings breakdown
    earnings = await db.agent_commissions.find({
        "agent_id": agent["_id"]
    }).sort([("created_at", -1)]).limit(12).to_list(length=12)
    
    # Get recent activity
    recent = await db.agent_activities.find({
        "agent_id": agent["_id"]
    }).sort([("created_at", -1)]).limit(10).to_list(length=10)
    
    return {
        "agent": {
            "id": str(agent["_id"]),
            "full_name": agent["full_name"],
            "agent_code": agent["agent_code"],
            "tier": agent["tier"],
            "wallet_balance": agent.get("wallet_balance", 0),
            "total_earnings": agent.get("total_earnings", 0)
        },
        "stats": {
            "total_referrals": total_referrals,
            "active_referrals": active_referrals,
            "commission_rate": agent.get("commission_rate", 0.15) * 100,
            "tier_progress": min((active_referrals / 1000) * 100, 100),
            "users_needed": max(0, 1000 - active_referrals)
        },
        "recent_activity": [
            {
                "id": str(a["_id"]),
                "description": a["description"],
                "type": a["type"],
                "date": a["created_at"]
            }
            for a in recent
        ],
        "earnings": [
            {
                "month": e["month"],
                "amount": e["total_paid"]
            }
            for e in earnings
        ]
    }

@router.get("/referrals")
async def get_agent_referrals(
    current_agent = Depends(get_current_user)
):
    """Get agent's referrals"""
    db = get_database()
    
    referrals = await db.users.find({
        "agent_id": current_agent["_id"]
    }).sort([("created_at", -1)]).to_list(length=100)
    
    return [
        {
            "id": str(r["_id"]),
            "username": r["username"],
            "email": r["email"],
            "is_active": r.get("is_active", False),
            "created_at": r["created_at"]
        }
        for r in referrals
    ]

@router.get("/earnings")
async def get_agent_earnings(
    current_agent = Depends(get_current_user)
):
    """Get agent's earnings history"""
    db = get_database()
    
    earnings = await db.agent_commissions.find({
        "agent_id": current_agent["_id"]
    }).sort([("created_at", -1)]).to_list(length=50)
    
    return [
        {
            "id": str(e["_id"]),
            "month": e["month"],
            "total_active_users": e.get("total_active_users", 0),
            "commission_amount": e.get("commission_amount", 0),
            "bonus_amount": e.get("bonus_amount", 0),
            "total_paid": e["total_paid"],
            "status": e.get("status", "paid"),
            "created_at": e["created_at"]
        }
        for e in earnings
    ]

@router.post("/withdraw")
async def request_withdrawal(
    amount: float = Query(..., gt=0),
    bank_name: str = Query(...),
    account_name: str = Query(...),
    account_number: str = Query(...),
    current_agent = Depends(get_current_user)
):
    """Request withdrawal"""
    db = get_database()
    
    agent = await db.agents.find_one({"_id": current_agent["_id"]})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if amount < 5000:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is UGX 5,000")
    
    if amount > agent.get("wallet_balance", 0):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create withdrawal request
    withdrawal = {
        "agent_id": current_agent["_id"],
        "amount": amount,
        "bank_name": bank_name,
        "account_name": account_name,
        "account_number": account_number,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db.withdrawals.insert_one(withdrawal)
    
    # Deduct from wallet
    await db.agents.update_one(
        {"_id": current_agent["_id"]},
        {"$inc": {"wallet_balance": -amount}}
    )
    
    return {
        "message": "Withdrawal request submitted successfully",
        "withdrawal_id": str(result.inserted_id),
        "amount": amount,
        "status": "pending"
    }