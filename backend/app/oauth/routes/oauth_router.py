# app/social/routes/oauth_router.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional
from datetime import datetime, timedelta

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

# Store state tokens with expiration (use Redis in production)
state_store: Dict[str, Dict] = {}


def add_state_to_store(state_token: str, user_id: int, platform: str):
    """Add state to store with expiration"""
    state_store[state_token] = {
        "user_id": user_id,
        "platform": platform,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=10)  # 10 minute expiration
    }


def get_state_from_store(state_token: str) -> Optional[Dict]:
    """Get state from store with expiration check"""
    if state_token not in state_store:
        return None

    state_data = state_store[state_token]

    # Check if state has expired
    if datetime.now() > state_data["expires_at"]:
        # Clean up expired state
        if state_token in state_store:
            del state_store[state_token]
        return None

    return state_data


def cleanup_expired_states():
    """Clean up expired states from store"""
    expired_states = []
    current_time = datetime.now()

    for state_token, state_data in state_store.items():
        if current_time > state_data["expires_at"]:
            expired_states.append(state_token)

    for state_token in expired_states:
        del state_store[state_token]

    if expired_states:
        print(f"Cleaned up {len(expired_states)} expired states")


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

    # Clean up expired states before adding new one
    cleanup_expired_states()

    # Generate state token
    state_token = oauth_service.generate_state_token()

    # Store state with user info and expiration
    add_state_to_store(state_token, current_user.id, platform)

    print(f"State stored: {state_token}")
    print(f"Current states in store: {len(state_store)}")

    # Generate OAuth URL
    if platform == "facebook":
        auth_url = oauth_service.get_facebook_auth_url(state_token)
    else:  # instagram
        auth_url = oauth_service.get_instagram_auth_url(state_token)

    print(f"Generated auth URL for {platform}")

    return {"auth_url": auth_url}


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
    """OAuth callback endpoint - handles both Facebook and Instagram"""

    print(f"\n=== CALLBACK HIT ===")
    print(f"Platform from URL: {platform}")
    print(f"Code received (first 50 chars): {code[:50]}...")
    print(f"State received: {state}")
    print(f"Total states in store: {len(state_store)}")

    # Verify state exists and is valid
    state_data = get_state_from_store(state)
    if not state_data:
        print(f"❌ State validation FAILED for token: {state}")
        print(f"Available states: {list(state_store.keys())}")

        # Clean up any expired states
        cleanup_expired_states()

        error_msg = "Invalid or expired state token. Please try connecting again."
        frontend_url = f"{settings.FRONTEND_URL}/dashboard?social_linked={platform}&error={error_msg}"
        return RedirectResponse(url=frontend_url)

    user_id = state_data["user_id"]
    actual_platform = state_data["platform"]  # Use platform from state store, not URL

    print(f"✅ State validated - User ID: {user_id}, Platform: {actual_platform}")

    # Remove used state immediately
    if state in state_store:
        del state_store[state]
        print(f"State removed from store: {state}")

    try:
        # Exchange code for tokens
        print(f"Exchanging code for {actual_platform} tokens...")

        if actual_platform == "facebook":
            token_data = await oauth_service.exchange_facebook_code(code)
            print(f"✅ Facebook token exchange successful")
        else:  # instagram
            token_data = await oauth_service.exchange_instagram_code(code)
            print(f"✅ Instagram token exchange successful")

        print(f"Token data keys: {list(token_data.keys())}")

        # Save to database
        print(f"Saving {actual_platform} account to database for user {user_id}...")
        account = await social_service.create_social_account(
            db, user_id, token_data, actual_platform
        )

        print(f"✅ Account saved with ID: {account.id}")

        # Redirect to frontend with success message
        frontend_url = f"{settings.FRONTEND_URL}/dashboard?social_linked={actual_platform}&success=true"
        print(f"🔄 Redirecting to: {frontend_url}")
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        print(f"❌ OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()

        # Redirect to frontend with error
        error_msg = str(e)
        # URL encode the error message
        import urllib.parse
        encoded_error = urllib.parse.quote(error_msg)
        frontend_url = f"{settings.FRONTEND_URL}/dashboard?social_linked={platform}&error={encoded_error}"
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
    # Clean up expired states when checking status
    cleanup_expired_states()

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
        },
        "state_store": {
            "active_states": len(state_store)
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