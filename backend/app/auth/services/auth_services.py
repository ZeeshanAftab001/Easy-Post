# app/auth/services/auth_services.py
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Header
import os
import jwt
import httpx
from jwt import PyJWKClient
from dotenv import load_dotenv
from clerk_backend_api import Clerk

from ...core.database import get_db
from ...user.models.user import User
from ...user.services.user_service import get_user_by_email, create_user
from ...user.schemas.user import UserCreate

load_dotenv()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_ISSUER = os.getenv("CLERK_ISSUER")

if not CLERK_SECRET_KEY:
    CLERK_SECRET_KEY = "sk_test_..."

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

# JWKS setup
JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json" if CLERK_ISSUER else None
jwks_client = PyJWKClient(JWKS_URL) if JWKS_URL else None

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get current user by verifying Clerk session token with cached signing keys"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        if CLERK_ISSUER and jwks_client:
            # Use cached jwks_client
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=CLERK_ISSUER,
                options={"verify_aud": False},
                leeway=60  # Allow for 60 seconds of clock drift
            )
        else:
            # Dangerous Fallback
            payload = jwt.decode(token, options={"verify_signature": False}, leeway=60)
            print("!!! WARNING: Insecure auth check performed !!!")
            
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # If email not in payload, fetch from Clerk API with timeout
        if not email:
            print(f"Fetching email for Clerk User: {user_id}")
            clerk_user = clerk.users.get(user_id=user_id)
            email = clerk_user.email_addresses[0].email_address

        user = await get_user_by_email(db, email=email)
        
        if user is None:
            print(f"JIT Provisioning new user: {email}")
            user_create = UserCreate(
                username=payload.get("username") or f"user_{user_id[:8]}",
                email=email,
                password="clerk_managed",
                whatsapp_number="TBD",
                niche="General"
            )
            user = await create_user(db, user_create)
            
        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except Exception as e:
        import traceback
        print(f"!!! HANDSHAKE CRASH !!!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        # If it is a JWT error, it will tell us why (e.g. invalid issuer)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Security Handshake Failed: {str(e)}",
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive node")
    return current_user