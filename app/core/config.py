"""Configuration module."""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Trading Bot API"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    DATABASE_URL: str | None = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Trading
    BINANCE_API_KEY: str
    BINANCE_API_SECRET: str
    TRADING_MODE: str = "test"
    MAX_POSITION_SIZE: float = 1000.0
    RISK_PERCENTAGE: float = 1.0

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, v: str | None, values) -> str:
        """Construct database URL from components."""
        if v:
            return v
        
        return (
            f"postgresql://{values.data['POSTGRES_USER']}:"
            f"{values.data['POSTGRES_PASSWORD']}@"
            f"{values.data['POSTGRES_SERVER']}:"
            f"{values.data['POSTGRES_PORT']}/"
            f"{values.data['POSTGRES_DB']}"
        )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )


settings = Settings()
