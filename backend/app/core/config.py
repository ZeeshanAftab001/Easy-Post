# app/core/config.py
import os

from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/EasyPost"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Whatsapp
    ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN")
    PHONE_NUMBER_ID : str = os.getenv("PHONE_NUMBER_ID")
    VERIFY_TOKEN : str = os.getenv("VERIFY_TOKEN")

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

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()