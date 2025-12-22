from mcp.server.fastmcp import FastMCP
from ..core.database import AsyncSessionLocal
from ..oauth.models.social import SocialAccount
from ..oauth.services.social_account_service import (
    get_active_instagram_account,
    is_token_expired,
    refresh_instagram_token
)
from .instagram import InstagramClient

mcp = FastMCP("Instagram MCP")


async def get_instagram_client(user_id: int) -> InstagramClient:
    """Fetch Instagram client for a user from DB at runtime, refresh token if needed"""
    async with AsyncSessionLocal() as db:  # Use your async session factory
        account = await get_active_instagram_account(db, user_id)

        if not account:
            raise ValueError(f"Instagram account not connected for user {user_id}")

        if is_token_expired(account):
            try:
                account = await refresh_instagram_token(account, db)
            except Exception as e:
                raise ValueError(f"Failed to refresh token: {e}")

        return InstagramClient(
            access_token=account.access_token,
            instagram_account_id=account.instagram_account_id,
            pages=account.pages
        )


# ---------------- MCP TOOLS ---------------- #

@mcp.tool()
async def verify_instagram_connection(user_id: int):
    client = await get_instagram_client(user_id)
    return await client.verify_connection()


@mcp.tool()
async def get_instagram_profile(user_id: int):
    client = await get_instagram_client(user_id)
    return await client.get_profile()


@mcp.tool()
async def get_instagram_posts(user_id: int, limit: int = 5):
    client = await get_instagram_client(user_id)
    return await client.get_posts(limit)


@mcp.tool()
async def create_instagram_post(user_id: int, image_url: str, caption: str = ""):
    client = await get_instagram_client(user_id)
    return await client.create_post(image_url, caption)


# ---------------- RUN MCP ---------------- #

if __name__ == "__main__":
    mcp.run()
