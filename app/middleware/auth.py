from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.session_service import SessionService
import logging

logger = logging.getLogger(__name__)

class SessionValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        public_routes = ["/health", "/api/docs", "/api/redoc", "/openapi.json"]
        if request.url.path in public_routes:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            session_service = SessionService()
            session_data = await session_service.validate_session(token)
            
            if not session_data:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
            
            if not session_data["session"].get("is_active", False):
                raise HTTPException(status_code=401, detail="Session has been terminated")
            
            request.state.user = session_data["user"]
            request.state.session = session_data["session"]
        
        return await call_next(request)