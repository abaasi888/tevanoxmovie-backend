from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import get_database
from app.services.dividend_service import DividendService

router = APIRouter()

async def get_current_user():
    # Placeholder - will be replaced with actual auth
    return {"_id": "user123", "username": "testuser", "email": "test@example.com", "is_admin": True}

async def require_admin(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/dividends/declare")
async def declare_dividend(
    total_dividend_pool: float = Query(..., gt=0),
    payment_date: Optional[datetime] = None,
    notes: Optional[str] = None,
    current_user = Depends(require_admin)
):
    """Declare a dividend (admin only)"""
    dividend_service = DividendService()
    
    result = await dividend_service.declare_dividend({
        "total_dividend_pool": total_dividend_pool,
        "payment_date": payment_date or datetime.utcnow() + timedelta(days=30),
        "notes": notes
    })
    
    return result

@router.get("/dividends")
async def get_all_dividends(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_admin)
):
    """Get all dividends (admin only)"""
    db = get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    total = await db.dividends.count_documents(query)
    dividends = await db.dividends.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    return {
        "data": [
            {
                "id": str(d["_id"]),
                "shareholder_id": str(d["shareholder_id"]),
                "amount": d["amount"],
                "dividend_per_share": d["dividend_per_share"],
                "shares_held": d["shares_held"],
                "status": d["status"],
                "payment_date": d["payment_date"],
                "declaration_date": d["declaration_date"]
            }
            for d in dividends
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/dividends/my")
async def get_my_dividends(current_user = Depends(get_current_user)):
    """Get current user's dividends"""
    db = get_database()
    
    shareholder = await db.shareholders.find_one({"user_id": current_user["_id"]})
    if not shareholder:
        return {"message": "You are not a shareholder"}
    
    dividends = await db.dividends.find({
        "shareholder_id": str(shareholder["_id"])
    }).sort("declaration_date", -1).to_list(length=50)
    
    return [
        {
            "id": str(d["_id"]),
            "amount": d["amount"],
            "dividend_per_share": d["dividend_per_share"],
            "shares_held": d["shares_held"],
            "status": d["status"],
            "payment_date": d["payment_date"],
            "declaration_date": d["declaration_date"],
            "reinvested": d.get("reinvested", False)
        }
        for d in dividends
    ]

@router.post("/dividends/{dividend_id}/pay")
async def process_dividend_payment(
    dividend_id: str,
    current_user = Depends(require_admin)
):
    """Process dividend payment (admin only)"""
    dividend_service = DividendService()
    result = await dividend_service.process_dividend_payment(dividend_id)
    
    return result

@router.post("/dividends/{dividend_id}/reinvest")
async def reinvest_dividend(
    dividend_id: str,
    current_user = Depends(get_current_user)
):
    """Reinvest dividend into shares"""
    db = get_database()
    
    # Verify shareholder owns this dividend
    dividend = await db.dividends.find_one({"_id": ObjectId(dividend_id)})
    if not dividend:
        raise HTTPException(status_code=404, detail="Dividend not found")
    
    shareholder = await db.shareholders.find_one({"_id": ObjectId(dividend["shareholder_id"])})
    if not shareholder:
        raise HTTPException(status_code=404, detail="Shareholder not found")
    
    # Check if user owns this shareholder
    if shareholder["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    dividend_service = DividendService()
    result = await dividend_service.process_dividend_reinvestment(dividend_id)
    
    return result

@router.get("/dividends/declarations")
async def get_dividend_declarations(
    current_user = Depends(require_admin)
):
    """Get all dividend declarations (admin only)"""
    db = get_database()
    
    declarations = await db.dividend_declarations.find().sort("declaration_date", -1).to_list(length=50)
    
    return [
        {
            "id": str(d["_id"]),
            "total_dividend_pool": d["total_dividend_pool"],
            "dividend_per_share": d["dividend_per_share"],
            "total_shares": d["total_shares"],
            "declaration_date": d["declaration_date"],
            "payment_date": d["payment_date"],
            "status": d["status"],
            "notes": d.get("notes")
        }
        for d in declarations
    ]
