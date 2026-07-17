import requests
import uuid
from datetime import datetime
from typing import Dict, Optional
from app.core.config import settings

class PaymentService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"
    
    def initialize_payment(
        self,
        email: str,
        amount: float,
        metadata: Dict = None,
        callback_url: str = None
    ) -> Dict:
        """Initialize a payment with Paystack"""
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        reference = f"TM-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        data = {
            "email": email,
            "amount": int(amount * 100),
            "reference": reference,
            "callback_url": callback_url or f"{settings.WEB_URL}/payment/confirm",
            "metadata": metadata or {}
        }
        
        response = requests.post(
            f"{self.base_url}/transaction/initialize",
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
    
    def verify_payment(self, reference: str) -> Dict:
        """Verify a payment with Paystack"""
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        
        response = requests.get(
            f"{self.base_url}/transaction/verify/{reference}",
            headers=headers
        )
        
        result = response.json()
        
        if result.get("status"):
            data = result["data"]
            return {
                "success": True,
                "status": data["status"],
                "amount": data["amount"] / 100,
                "reference": reference,
                "metadata": data.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Verification failed")
            }
    
    def initiate_mobile_money_payment(
        self,
        email: str,
        amount: float,
        phone: str,
        provider: str
    ) -> Dict:
        """Initiate mobile money payment"""
        metadata = {
            "phone": phone,
            "provider": provider,
            "payment_method": "mobile_money"
        }
        
        return self.initialize_payment(email, amount, metadata)
    
    def initiate_card_payment(
        self,
        email: str,
        amount: float,
        metadata: Dict = None
    ) -> Dict:
        """Initiate card payment"""
        return self.initialize_payment(email, amount, metadata)