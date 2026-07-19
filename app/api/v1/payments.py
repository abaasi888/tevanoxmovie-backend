from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
import uuid
import requests
from app.core.database import get_database
from app.api.v1.auth import get_current_user
from app.core.config import settings

router = APIRouter()

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY

@router.get("/methods")
async def get_payment_methods():
    """Get available payment methods"""
    return {
        "methods": [
            {
                "id": "mobile_money",
                "name": "Mobile Money",
                "icon": "phone-android",
                "providers": [
                    {"id": "mtn", "name": "MTN Mobile Money", "color": "#FFD700"},
                    {"id": "airtel", "name": "Airtel Money", "color": "#FF0000"},
                    {"id": "africell", "name": "Africell Money", "color": "#00FF00"}
                ]
            },
            {
                "id": "visa",
                "name": "Visa / Credit Card",
                "icon": "credit-card",
                "providers": [
                    {"id": "visa", "name": "Visa"},
                    {"id": "mastercard", "name": "Mastercard"},
                    {"id": "amex", "name": "American Express"}
                ]
            }
        ]
    }

@router.post("/initialize")
async def initialize_payment(
    amount: float,
    plan: str,
    payment_method: str,
    phone_number: Optional[str] = None,
    provider: Optional[str] = None,
    email: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Initialize a payment"""
    if payment_method == "mobile_money" and not phone_number:
        raise HTTPException(status_code=400, detail="Phone number required for Mobile Money")
    
    reference = f"TM-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Prepare Paystack request
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "amount": int(amount * 100),  # Convert to cents
        "email": email or current_user["email"],
        "reference": reference,
        "callback_url": f"{settings.WEB_URL}/payment/confirm",
        "metadata": {
            "user_id": str(current_user["_id"]),
            "plan": plan,
            "payment_method": payment_method,
            "phone_number": phone_number,
            "provider": provider
        }
    }
    
    # For mobile money, add mobile money specific fields
    if payment_method == "mobile_money" and provider:
        data["mobile_money"] = {
            "phone": phone_number,
            "provider": provider
        }
    
    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=data,
            headers=headers
        )
        
        result = response.json()
        
        if result.get("status"):
            return {
                "success": True,
                "reference": reference,
                "authorization_url": result["data"]["authorization_url"],
                "access_code": result["data"]["access_code"]
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Payment initialization failed")
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment initialization error: {str(e)}")

@router.get("/verify/{reference}")
async def verify_payment(
    reference: str,
    current_user = Depends(get_current_user)
):
    """Verify a payment"""
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }
    
    try:
        response = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}",
            headers=headers
        )
        
        result = response.json()
        
        if result.get("status"):
            data = result["data"]
            
            # If payment successful, activate subscription
            if data["status"] == "success":
                db = get_database()
                
                # Check if subscription already activated
                existing = await db.subscriptions.find_one({
                    "transaction_id": reference
                })
                
                if not existing:
                    # Get plan from metadata
                    metadata = data.get("metadata", {})
                    plan = metadata.get("plan", "monthly")
                    
                    # Activate subscription (logic in subscriptions.py)
                    # This would call the subscription activation function
                    
                    return {
                        "success": True,
                        "status": data["status"],
                        "amount": data["amount"] / 100,
                        "reference": reference
                    }
                else:
                    return {
                        "success": True,
                        "status": "already_processed",
                        "reference": reference
                    }
            else:
                return {
                    "success": False,
                    "status": data["status"],
                    "reference": reference
                }
        else:
            return {
                "success": False,
                "error": result.get("message", "Verification failed"),
                "reference": reference
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification error: {str(e)}")

@router.get("/history")
async def get_payment_history(
    current_user = Depends(get_current_user)
):
    """Get user's payment history"""
    db = get_database()
    
    payments = await db.payments.find({
        "user_id": current_user["_id"]
    }).sort([("created_at", -1)]).to_list(length=50)
    
    return [
        {
            "id": str(p["_id"]),
            "amount": p["amount"],
            "plan": p.get("plan"),
            "status": p.get("status"),
            "payment_method": p.get("payment_method"),
            "reference": p.get("reference"),
            "created_at": p["created_at"]
        }
        for p in payments
    ]