# app/social/services/social_service.py
from typing import List, Optional, Dict
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from  ..models.social import SocialAccount

class SocialAccountService:

    # In social_service.py - Update create_social_account method

    async def create_social_account(
            self,
            db: AsyncSession,
            user_id: int,
            data: Dict,
            platform: str
    ) -> SocialAccount:
        """Create or update social account"""

        print(f"\n=== CREATE SOCIAL ACCOUNT DEBUG ===")
        print(f"Platform: {platform}")
        print(f"Data keys: {list(data.keys())}")
        print(f"User ID in data: {data.get('user_id')}")

        # Check if account already exists
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform == platform
            )
        )
        existing = result.scalar_one_or_none()

        # Ensure we have a platform_user_id
        platform_user_id = data.get('user_id')
        if not platform_user_id:
            # Create a fallback ID for Instagram if missing
            if platform == 'instagram':
                import hashlib
                access_token = data.get('access_token', '')
                platform_user_id = f"insta_{hashlib.md5(access_token.encode()).hexdigest()[:16]}"
            else:
                platform_user_id = f"unknown_{platform}"

        print(f"Using platform_user_id: {platform_user_id}")

        if existing:
            # Update existing account
            existing.access_token = data['access_token']
            existing.refresh_token = data.get('refresh_token')
            existing.token_expires_at = datetime.now() + timedelta(seconds=data.get('expires_in', 3600))
            existing.platform_user_id = platform_user_id
            existing.pages = json.dumps(data.get('pages', [])) if data.get('pages') else None

            if platform == 'instagram':
                existing.instagram_account_id = data.get('instagram_account_id')

            existing.updated_at = datetime.now()
            await db.commit()
            await db.refresh(existing)
            return existing

        # Create new account
        expires_at = None
        if 'expires_in' in data:
            expires_at = datetime.now() + timedelta(seconds=data['expires_in'])

        db_account = SocialAccount(
            user_id=user_id,
            platform=platform,
            platform_user_id=platform_user_id,  # Use the ensured ID
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            token_expires_at=expires_at,
            pages=json.dumps(data.get('pages', [])) if data.get('pages') else None,
            instagram_account_id=data.get('instagram_account_id'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(db_account)
        await db.commit()
        await db.refresh(db_account)
        return db_account

    async def get_user_social_accounts(
            self,
            db: AsyncSession,
            user_id: int
    ) -> List[SocialAccount]:
        """Get all social accounts for a user"""
        result = await db.execute(
            select(SocialAccount).where(SocialAccount.user_id == user_id)
        )
        return result.scalars().all()

    async def get_social_account_by_platform(
            self,
            db: AsyncSession,
            user_id: int,
            platform: str
    ) -> Optional[SocialAccount]:
        """Get specific platform account for user"""
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.user_id == user_id,
                SocialAccount.platform == platform
            )
        )
        return result.scalar_one_or_none()