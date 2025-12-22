
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime  # <-- Make sure to import datetime
from ...auth.utils.auth_utils import get_password_hash
from ...user.models.user import User
from ...user.schemas.user import UserCreate
from sqlalchemy import select


async def get_users(db: AsyncSession):
    """Get all users (async)"""
    result = await db.execute(select(User))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int):
    """Get user by ID (async)"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_number(db: AsyncSession, phone_number: str):
    """Get user by WhatsApp phone number"""
    result = await db.execute(
        select(User).where(User.whatsapp_number == phone_number)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    """Get user by email (async)"""
    
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user (async)"""
    # Get current timestamp
    now = datetime.utcnow()
    
    db_user = User(
        email=str(user.email),
        username=user.username,
        password=get_password_hash(user.password),
        whatsapp_number=user.whatsapp_number,
        niche=user.niche,
        created_at=now,  # <-- Add this
        updated_at=now   # <-- Add this
        # is_active=True is already set by default in the model
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    """Delete a user (async)"""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if db_user:
        await db.delete(db_user)
        await db.commit()
    
    return db_user

# In your user_service.py
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()