import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Browser configuration
    max_browsers: int = 20
    port_start: int = 9100
    port_end: int = 9120
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Environment
    env: str = "development"
    
    # CDP configuration
    cdp_timeout: int = 30

    # ... existing ...
    database_type: str = "mongodb"  # mongodb | postgresql | sqlite | mysql
    database_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "sharkbrowser"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

