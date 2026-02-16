# app/oauth/services/social_account_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.oauth.models.social import SocialAccount
import logging

logger = logging.getLogger(__name__)

async def get_active_facebook_account(
    db: AsyncSession,
    user_id: int
) -> SocialAccount | None:
    """Get active Facebook account for user."""
    stmt = select(SocialAccount).where(
        SocialAccount.user_id == user_id,
        SocialAccount.platform == "facebook",
        SocialAccount.is_active == True
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
    return account