from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "tevanoxmovie"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Domain
    DOMAIN: str = "tevanox.com"
    API_URL: str = "https://api.tevanox.com"
    WEB_URL: str = "https://tevanox.com"
    ADMIN_URL: str = "https://admin.tevanox.com"
    MOBILE_URL: str = "https://mobile.tevanox.com"  # Added
    AGENT_URL: str = "https://agent.tevanox.com"    # Added
    STORAGE_URL: str = "https://storage.tevanox.com" # Added
    
    # Storage
    STORAGE_ENDPOINT: str
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str
    STORAGE_BUCKET: str = "tevanoxmovie"
    
    # Payment
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str
    
    # Commission
    TEVANOX_SHARE: float = 0.60
    NETWORK_TOTAL: float = 0.40
    LEVEL_1_COMMISSION: float = 0.25
    LEVEL_2_COMMISSION: float = 0.10
    LEVEL_3_COMMISSION: float = 0.05
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return [
            self.WEB_URL,
            self.ADMIN_URL,
            self.MOBILE_URL,
            self.AGENT_URL,
            self.STORAGE_URL,
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8081",
            "http://localhost:8082",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8081",
            "http://127.0.0.1:8082",
        ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()