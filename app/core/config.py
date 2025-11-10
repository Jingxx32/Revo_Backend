from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import List, Any
import os
import json

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/revo_db"
    
    # Security
    # JWT_SECRET_KEY can be set via environment variable JWT_SECRET_KEY or SECRET_KEY (for backward compatibility)
    # pydantic-settings automatically reads from environment variables
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time in minutes
    
    # CORS
    # CORS_ORIGINS can be set via environment variable as comma-separated string or JSON array
    # Example (comma-separated): CORS_ORIGINS="http://localhost:3000,http://w22c236sqg.free.wtbusaym.site"
    # Example (JSON): CORS_ORIGINS='["http://localhost:3000","http://w22c236sqg.free.wtbusaym.site"]'
    # Default includes localhost and the frontend URL
    CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://w22c236sqg.free.wtbusaym.site",
        "https://w22c236sqg.free.wtbusaym.site",  # Also support HTTPS
    ]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS_ORIGINS from string (comma-separated or JSON) to list."""
        # If v is already a list, return it
        if isinstance(v, list):
            return v
        
        # If v is a string, parse it
        if isinstance(v, str):
            try:
                # Try to parse as JSON array first
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                # If JSON parsing fails, treat as comma-separated string
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        # For any other type, return as-is (should not happen, but safe fallback)
        return v
    
    @model_validator(mode='after')
    def handle_secret_key(self):
        """Support SECRET_KEY environment variable for backward compatibility."""
        secret_key_env = os.getenv("SECRET_KEY")
        if secret_key_env:
            self.JWT_SECRET_KEY = secret_key_env
        return self
    
    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your_stripe_publishable_key"
    
    # AWS S3 (for photo storage)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email (for notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

