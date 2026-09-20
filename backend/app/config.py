import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "MediScan AI: Intelligent Drug Repurposing Research Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = Field(default="mediscan-super-secure-secret-key-production-change-me-32chars!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./mediscan.db")
    
    # External API Keys (Optional with graceful public fallbacks)
    NCBI_API_KEY: Optional[str] = None
    USER_EMAIL: Optional[str] = "researcher@mediscan.ai"
    FDA_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # AI / LLM Configuration
    MODEL_PROVIDER: str = "grounded_extractive"  # "openai", "anthropic", "grounded_extractive"
    MODEL_NAME: str = "gpt-4o-mini"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
