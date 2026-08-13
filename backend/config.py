"""
Configuration for AgroControl Pro
Settings and environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App settings
    APP_NAME: str = "AgroControl Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/agrocontrol_pro"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-change-in-production-at-least-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:8000",
    ]
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 3000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
