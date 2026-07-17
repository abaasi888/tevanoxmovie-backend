from datetime import datetime, timedelta
from typing import Optional, Dict, List
import hashlib
import uuid
from app.core.database import get_database
import logging

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.db = get_database()
    
    def generate_device_id(self, user_agent: str, ip: str) -> str:
        combined = f"{user_agent}_{ip}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def create_session(self, user_id: str, device_type: str, 
                             device_name: str, user_agent: str = None,
                             ip_address: str = None) -> Dict:
        device_id = self.generate_device_id(
            user_agent or "Unknown",
            ip_address or "0.0.0.0"
        )
        
        existing_session = await self.db.sessions.find_one({
            "user_id": user_id,
            "device_id": device_id,
            "is_active": True
        })
        
        if existing_session:
            await self.db.sessions.update_one(
                {"_id": existing_session["_id"]},
                {
                    "$set": {
                        "last_activity": datetime.utcnow(),
                        "expires_at": datetime.utcnow() + timedelta(days=30)
                    }
                }
            )
            return {
                "session_id": str(existing_session["_id"]),
                "device_id": device_id,
                "is_new": False
            }
        
        await self.db.sessions.update_many(
            {
                "user_id": user_id,
                "is_active": True,
                "device_id": {"$ne": device_id}
            },
            {
                "$set": {
                    "is_active": False,
                    "ended_at": datetime.utcnow(),
                    "end_reason": "new_device_login"
                }
            }
        )
        
        token = str(uuid.uuid4())
        
        session = {
            "user_id": user_id,
            "token": token,
            "device_type": device_type,
            "device_name": device_name,
            "device_id": device_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "last_activity": datetime.utcnow()
        }
        
        result = await self.db.sessions.insert_one(session)
        session["_id"] = str(result.inserted_id)
        
        await self.db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "last_login": datetime.utcnow(),
                    "current_session_id": str(result.inserted_id),
                    "device_type": device_type,
                    "device_name": device_name
                }
            }
        )
        
        logger.info(f"Session created for user {user_id} on {device_type} ({device_name})")
        logger.info(f"All other sessions were invalidated")
        
        return {
            "session_id": str(result.inserted_id),
            "token": token,
            "device_id": device_id,
            "is_new": True
        }
    
    async def validate_session(self, token: str) -> Optional[Dict]:
        session = await self.db.sessions.find_one({
            "token": token,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        await self.db.sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
        
        user = await self.db.users.find_one({"_id": session["user_id"]})
        if not user:
            return None
        
        return {
            "user": user,
            "session": session
        }
    
    async def invalidate_session(self, token: str) -> bool:
        result = await self.db.sessions.update_one(
            {"token": token},
            {
                "$set": {
                    "is_active": False,
                    "ended_at": datetime.utcnow(),
                    "end_reason": "user_logout"
                }
            }
        )
        return result.modified_count > 0
    
    async def invalidate_other_sessions(self, user_id: str, session_id: str) -> int:
        result = await self.db.sessions.update_many(
            {
                "user_id": user_id,
                "is_active": True,
                "_id": {"$ne": session_id}
            },
            {
                "$set": {
                    "is_active": False,
                    "ended_at": datetime.utcnow(),
                    "end_reason": "terminated_by_user"
                }
            }
        )
        return result.modified_count
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        sessions = await self.db.sessions.find({
            "user_id": user_id,
            "is_active": True
        }).sort("created_at", -1).to_list(length=10)
        
        return [
            {
                "id": str(s["_id"]),
                "device_type": s["device_type"],
                "device_name": s["device_name"],
                "created_at": s["created_at"],
                "last_activity": s["last_activity"],
                "is_current": s.get("is_current", False)
            }
            for s in sessions
        ]