"""
Configuration management for NER-LOGIX
"""

from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "NER-LOGIX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_TYPE: str = "json"  # json or postgresql
    
    # PostgreSQL (for future use)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nerlogix"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # Risk thresholds
    RISK_LOW_THRESHOLD: int = 30
    RISK_MEDIUM_THRESHOLD: int = 60
    RISK_HIGH_THRESHOLD: int = 80
    
    # Simulation
    SIMULATION_INTERVAL: float = 1.0  # seconds
    VEHICLE_SPEED: float = 60.0  # km/h
    
    # WebSocket
    WS_MAX_SIZE: int = 4096
    WS_PING_INTERVAL: int = 20
    WS_PING_TIMEOUT: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()