# app/social/routes/oauth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import json

from ...auth.services.auth_services import get_current_user
from ...core.database import get_db
from ...core.config import settings
from ...user.models.user import User

from ..models.social import SocialAccount
from ..services.oauth_service import OAuthService
from ..services.social_service import SocialAccountService

oauth_router = APIRouter(prefix="/social", tags=["social-auth"])
oauth_service = OAuthService()
social_service = SocialAccountService()

# Store state tokens temporarily (use Redis in production)
state_store: Dict[str, Dict] = {}


@oauth_router.get("/auth/{platform}/init")
async def init_oauth(
        platform: str,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Initiate OAuth flow for Facebook or Instagram"""
    print(f"\n=== INIT OAUTH DEBUG ===")
    print(f"Platform: {platform}")
    print(f"User ID: {current_user.id}")
    print(f"Username: {current_user.username}")
    if platform not in ["facebook", "instagram"]:
        raise HTTPException(status_code=400, detail="Invalid platform")

    # Generate state token
    state_token = oauth_service.generate_state_token()

    # Store state with user info
    state_store[state_token] = {
        "user_id": current_user.id,
        "platform": platform
    }


    # Generate OAuth URL
    if platform == "facebook":
        auth_url = oauth_service.get_facebook_auth_url(state_token)
    else:  # instagram
        auth_url = oauth_service.get_instagram_auth_url(state_token)

    return {"auth_url": auth_url}


# Add a new endpoint in your router for frontend to call
@oauth_router.post("/auth/facebook/exchange")
async def exchange_facebook_code(
        code_data: dict,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Exchange Facebook code for tokens (called from frontend)"""
    try:
        code = code_data.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="No code provided")

        # Exchange code for tokens
        token_data = await oauth_service.exchange_facebook_code(code)

        # Save to database
        account = await social_service.create_social_account(
            db, current_user.id, token_data, "facebook"
        )

        return {
            "success": True,
            "message": "Facebook account connected successfully",
            "account": {
                "id": account.id,
                "platform": account.platform,
                "platform_user_id": account.platform_user_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@oauth_router.get("/auth/{platform}/callback")
async def oauth_callback(
        platform: str,
        code: str,
        state: str,
        db: AsyncSession = Depends(get_db)
):
    """OAuth callback endpoint"""

    # Verify state
    if state not in state_store:
        raise HTTPException(status_code=400, detail="Invalid state token")

    state_data = state_store.pop(state)
    user_id = state_data["user_id"]
    print(user_id )
    """OAuth callback endpoint"""

    print(f"\n=== CALLBACK HIT ===")
    print(f"Platform: {platform}")
    print(f"Code received: {code}")
    print(f"State received: {state}")
    print(f"State in store: {state in state_store}")
    try:
        # Exchange code for tokens
        if platform == "facebook":
            token_data = await oauth_service.exchange_facebook_code(code)
            print(token_data)
        else:  # instagram
            token_data = await oauth_service.exchange_instagram_code(code)

        # Save to database
        account = await social_service.create_social_account(
            db, user_id, token_data, platform
        )

        # Redirect to frontend with success message
        frontend_url = f"{settings.FRONTEND_URL}/dashboard?social_linked={platform}&success=true"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        # Redirect to frontend with error
        frontend_url = f"{settings.FRONTEND_URL}/dashboard?social_linked={platform}&error={str(e)}"
        return RedirectResponse(url=frontend_url)





@oauth_router.get("/accounts")
async def get_linked_accounts(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all linked social accounts for current user"""
    accounts = await social_service.get_user_social_accounts(db, current_user.id)
    return accounts
@oauth_router.get("/status")
async def oauth_status():
    """Check OAuth configuration status"""
    return {
        "status": "online",
        "endpoints": {
            "facebook_init": "/api/oauth/social/auth/facebook/init",
            "facebook_callback": "/api/oauth/social/auth/facebook/callback",
            "instagram_init": "/api/oauth/social/auth/instagram/init",
            "instagram_callback": "/api/oauth/social/auth/instagram/callback"
        },
        "configured": {
            "facebook": bool(settings.FACEBOOK_APP_ID and settings.FACEBOOK_APP_SECRET),
            "instagram": bool(settings.INSTAGRAM_APP_ID and settings.INSTAGRAM_APP_SECRET)
        }
    }

@oauth_router.delete("/accounts/{platform}")
async def unlink_account(
        platform: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Unlink social account"""
    result = await db.execute(
        select(SocialAccount).where(
            SocialAccount.user_id == current_user.id,
            SocialAccount.platform == platform
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await db.delete(account)
    await db.commit()

    return {"message": f"{platform} account unlinked successfully"}