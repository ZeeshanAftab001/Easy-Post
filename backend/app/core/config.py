# app/core/config.py
import os

from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_KLn6PoJtSsX8@ep-weathered-flower-ad1iqgws-pooler.c-2.us-east-1.aws.neon.tech/EasyPostSAAS?ssl=require"
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Clerk
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_WEBHOOK_SECRET: Optional[str] = None
    CLERK_ISSUER: Optional[str] = None

    # WAHA (WhatsApp HTTP API) - Replaces Meta Cloud API
    WAHA_URL: str = os.getenv("WAHA_URL", "http://localhost:3000")
    WAHA_SESSION: str = os.getenv("WAHA_SESSION", "default")
    WAHA_API_KEY: Optional[str] = os.getenv("WAHA_API_KEY", None)
    VERIFY_TOKEN : str = os.getenv("VERIFY_TOKEN", "zeeshanaftab")

    GOOGLE_API_KEY : str = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY : str = os.getenv("OPENAI_API_KEY")
    # Facebook OAuth - Make optional for now
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: str = "http://localhost:5173/auth/facebook/callback"

    # Instagram OAuth - Make optional for now
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:5173/auth/instagram/callback"

    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME", "")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    FACEBOOK_GRAPH_VERSION: str = os.getenv("FACEBOOK_GRAPH_VERSION", "v19.0")
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()