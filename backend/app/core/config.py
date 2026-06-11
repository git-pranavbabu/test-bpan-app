from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "BPAN Battery Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    DATABASE_URL: str = "postgresql://bpan_user:bpan_password@localhost:5432/bpan_db"
    
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@hykonindia.com"
    ADMIN_PASSWORD: str = "admin_password"
    
    RATE_LIMIT_MAX_FAILURES: int = 5
    RATE_LIMIT_LOCKOUT_MINUTES: int = 15
    
    INITIAL_SERIAL: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
