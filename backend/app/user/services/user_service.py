
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime  # <-- Make sure to import datetime
from ...auth.utils.auth_utils import get_password_hash
from ...user.models.user import User
from ...user.schemas.user import UserCreate
from ...chat.services.whatsapp_service import send_verification_message
from sqlalchemy import select, or_


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


async def get_user_by_number_or_lid(db: AsyncSession, identifier: str):
    """Get user by WhatsApp phone number OR WAHA LID."""
    result = await db.execute(
        select(User).where(
            or_(
                User.whatsapp_number == identifier,
                User.whatsapp_lid == identifier
            )
        )
    )
    return result.scalar_one_or_none()


async def verify_user(db: AsyncSession, user: User, lid: str):
    """Mark user as verified and store their LID."""
    user.whatsapp_lid = lid
    user.verification_status = "verified"
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    print(f"✅ User {user.id} verified with LID {lid}")
    return user


async def save_whatsapp_lid(db: AsyncSession, user: User, lid: str):
    """Permanently store the WAHA LID on the user so future lookups succeed."""
    if user.whatsapp_lid != lid:
        user.whatsapp_lid = lid
        user.updated_at = datetime.utcnow()
        await db.commit()
        print(f"✅ Stored WAHA LID '{lid}' for user ID={user.id}")


async def get_user_by_email(db: AsyncSession, email: str):
    """Get user by email (async)"""
    
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user (async)"""
    now = datetime.utcnow()
    
    db_user = User(
        email=str(user.email),
        username=user.username,
        password=get_password_hash(user.password),
        whatsapp_number=user.whatsapp_number,
        niche=user.niche,
        verification_status="pending",
        created_at=now,
        updated_at=now
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Trigger verification message if phone number is provided and not "TBD"
    if db_user.whatsapp_number and db_user.whatsapp_number != "TBD":
        await send_verification_message(db_user.whatsapp_number)
    
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

async def update_user(db: AsyncSession, user_id: int, user_data: dict):
    """Update user details"""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if db_user:
        # Check if whatsapp_number is being changed
        new_number = user_data.get("whatsapp_number")
        number_changed = new_number and new_number != db_user.whatsapp_number

        for key, value in user_data.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        if number_changed:
            db_user.verification_status = "pending"
            db_user.whatsapp_lid = None # Reset LID for the new number
            print(f"🔄 Phone number changed for user {user_id}. Resetting verification status.")

        db_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_user)

        # Trigger verification message if number changed
        if number_changed and db_user.whatsapp_number != "TBD":
            await send_verification_message(db_user.whatsapp_number)
    
    return db_user