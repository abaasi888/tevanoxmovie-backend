from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.services.shareholder_service import ShareholderService

router = APIRouter()

async def get_current_user():
    # Placeholder - will be replaced with actual auth
    return {"_id": "user123", "username": "testuser", "email": "test@example.com", "is_admin": True}

async def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.get("/shareholders")
async def get_all_shareholders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_admin)
):
    """Get all shareholders (admin only)"""
    db = get_database()
    
    total = await db.shareholders.count_documents({})
    shareholders = await db.shareholders.find().skip(skip).limit(limit).to_list(length=limit)
    
    return {
        "data": [
            {
                "id": str(s["_id"]),
                "full_name": s["full_name"],
                "email": s["email"],
                "total_shares": s.get("total_shares", 0),
                "total_investment": s.get("total_investment", 0),
                "total_dividends_earned": s.get("total_dividends_earned", 0),
                "tier": s.get("tier", "bronze"),
                "is_active": s.get("is_active", True),
                "joined_date": s["joined_date"]
            }
            for s in shareholders
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/shareholders/my")
async def get_my_shareholder_info(current_user = Depends(get_current_user)):
    """Get current user's shareholder information"""
    db = get_database()
    
    shareholder = await db.shareholders.find_one({"user_id": current_user["_id"]})
    if not shareholder:
        return {"message": "You are not a shareholder"}
    
    shareholder_service = ShareholderService()
    dashboard = await shareholder_service.get_shareholder_dashboard(str(shareholder["_id"]))
    
    return dashboard

@router.post("/shareholders/purchase")
async def purchase_shares(
    shares: int = Query(..., gt=0),
    payment_method: str = "bank_transfer",
    current_user = Depends(get_current_user)
):
    """Purchase shares"""
    db = get_database()
    
    # Check if user is already a shareholder
    shareholder = await db.shareholders.find_one({"user_id": current_user["_id"]})
    
    if not shareholder:
        # Create new shareholder
        shareholder_service = ShareholderService()
        shareholder = await shareholder_service.create_shareholder({
            "user_id": current_user["_id"],
            "full_name": current_user["username"],
            "email": current_user["email"]
        })
    
    # Process purchase
    share_price = 15000  # Current price per share
    total_amount = shares * share_price
    
    shareholder_service = ShareholderService()
    result = await shareholder_service.purchase_shares(
        str(shareholder["_id"]),
        shares,
        share_price,
        payment_method
    )
    
    return result

@router.get("/shareholders/{shareholder_id}/dashboard")
async def get_shareholder_dashboard(
    shareholder_id: str,
    current_user = Depends(require_admin)
):
    """Get shareholder dashboard (admin only)"""
    shareholder_service = ShareholderService()
    dashboard = await shareholder_service.get_shareholder_dashboard(shareholder_id)
    
    return dashboard
