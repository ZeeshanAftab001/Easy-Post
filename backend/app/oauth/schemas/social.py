# app/social/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class SocialAccountBase(BaseModel):
    platform: str
    platform_user_id: str
    is_active: bool = True


class SocialAccountCreate(SocialAccountBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    pages: Optional[str] = None
    instagram_account_id: Optional[str] = None
    scopes: Optional[str] = None


class SocialAccountResponse(SocialAccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OAuthInitRequest(BaseModel):
    platform: str  # "facebook" or "instagram"


class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None