from datetime import datetime
from typing import Optional, List
from app.core.database import get_database
import uuid

class AgentService:
    def __init__(self):
        self.db = get_database()
    
    async def create_agent(self, agent_data: dict) -> dict:
        # Generate agent code
        agent_code = f"TVX-{uuid.uuid4().hex[:6].upper()}"
        agent_data["agent_code"] = agent_code
        agent_data["joined_date"] = datetime.utcnow()
        agent_data["tier"] = 1
        agent_data["commission_rate"] = 0.15
        agent_data["wallet_balance"] = 0
        agent_data["total_earnings"] = 0
        agent_data["is_active"] = True
        
        result = await self.db.agents.insert_one(agent_data)
        return {"id": str(result.inserted_id), **agent_data}
    
    async def get_agent_by_email(self, email: str) -> Optional[dict]:
        return await self.db.agents.find_one({"email": email})
    
    async def get_agent_by_code(self, agent_code: str) -> Optional[dict]:
        return await self.db.agents.find_one({"agent_code": agent_code})
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[dict]:
        return await self.db.agents.find_one({"_id": agent_id})
    
    async def update_wallet(self, agent_id: str, amount: float) -> None:
        await self.db.agents.update_one(
            {"_id": agent_id},
            {"$inc": {"wallet_balance": amount, "total_earnings": amount}}
        )
    
    async def get_referrals(self, agent_id: str) -> List[dict]:
        return await self.db.users.find({
            "agent_id": agent_id
        }).to_list(length=100)
    
    async def get_team_size(self, agent_id: str) -> int:
        return await self.db.users.count_documents({"agent_id": agent_id})