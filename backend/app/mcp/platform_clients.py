# app/mcp/platform_clients.py
"""
DB-backed credential helpers for each platform.
All MCP tools call these instead of accepting credentials as parameters.

Pattern mirrors get_instagram_client() in instagram_client.py.
"""
import json
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.oauth.models.social import SocialAccount
from app.oauth.services.oauth_service import OAuthService
from datetime import datetime

oauth_service = OAuthService()


async def _get_account(user_id: int, platform: str) -> SocialAccount:
    """Fetch active SocialAccount for a platform or raise ValueError."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform == platform,
                SocialAccount.is_active == True,
            )
        )
        account = result.scalars().first()
    if not account:
        raise ValueError(
            f"No active {platform} account found for user {user_id}. "
            f"Please connect your {platform.title()} account first."
        )

    # Global Token Refresh Check
    if account.token_expires_at and account.token_expires_at <= datetime.now():
        print(f"[*] Token for {platform} expired at {account.token_expires_at}. Current time: {datetime.now()}. Attempting refresh...")
        try:
            if platform in ["facebook", "instagram"]:
                refresh_data = await oauth_service.refresh_facebook_token(account.access_token)
                async with AsyncSessionLocal() as db:
                    # Update in DB
                    account.access_token = refresh_data['access_token']
                    if 'expires_in' in refresh_data:
                        from datetime import timedelta
                        account.token_expires_at = datetime.now() + timedelta(seconds=refresh_data['expires_in'])
                    db.add(account)
                    await db.commit()
                    await db.refresh(account)
                print(f"[OK] {platform} token refreshed successfully.")
        except Exception as e:
            print(f"[!] Failed to refresh {platform} token: {e}. Proceeding anyway as Page Tokens may still be valid.")

    return account


async def get_facebook_page_credentials(user_id: int) -> tuple[str, str]:
    """
    Returns (page_id, page_token) from the stored Facebook SocialAccount.
    Uses the first page in the pages JSON array.
    """
    account = await _get_account(user_id, "facebook")
    if not account.pages:
        raise ValueError("Facebook account has no pages. Please reconnect your Facebook account.")
    pages = json.loads(account.pages)
    if not pages:
        raise ValueError("No Facebook pages found.")
    page = pages[0]
    page_id    = page.get("id")
    page_token = page.get("access_token") or account.access_token
    if not page_id or not page_token:
        raise ValueError("Invalid Facebook page data (missing id or token).")
    return page_id, page_token