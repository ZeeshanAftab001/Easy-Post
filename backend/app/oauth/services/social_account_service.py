# app/oauth/services/social_account_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from ..models.social import SocialAccount

import httpx
from datetime import datetime, timedelta, timezone

from ...core.database import engine
from ...mcp.instagram import InstagramClient

async def get_active_instagram_account(
    db: AsyncSession,
    user_id: int
) -> SocialAccount | None:
    stmt = select(SocialAccount).where(
        SocialAccount.user_id == user_id,
        SocialAccount.platform == "instagram",
        SocialAccount.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalars().first()



def is_token_expired(account: SocialAccount) -> bool:
    if not account.token_expires_at:
        return False  # long-lived token
    return account.token_expires_at <= datetime.now(timezone.utc)



INSTAGRAM_REFRESH_URL = "https://graph.instagram.com/refresh_access_token"

async def refresh_instagram_token(account: SocialAccount, db: AsyncSession):
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": account.access_token
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(INSTAGRAM_REFRESH_URL, params=params)
        res.raise_for_status()
        data = res.json()

    account.access_token = data["access_token"]
    account.token_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=data["expires_in"]
    )

    await db.commit()
    await db.refresh(account)

    return account


