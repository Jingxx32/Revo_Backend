from pydantic_settings import BaseSettings
from typing import List
import os

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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Support SECRET_KEY environment variable for backward compatibility
        # Check SECRET_KEY first, then JWT_SECRET_KEY
        secret_key_env = os.getenv("SECRET_KEY")
        if secret_key_env:
            self.JWT_SECRET_KEY = secret_key_env
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
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

