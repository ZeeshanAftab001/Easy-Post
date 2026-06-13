from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from ...auth.services.auth_services import get_current_active_user
from ...core.database import get_db
from ...user.models.user import User
from ...user.schemas.user import UserSchema, UserCreate
from ...user.services.user_service import (
    get_users,
    get_user,
    delete_user,
    create_user,
    get_user_by_email, 
    get_user_by_username,
    update_user,
    verify_user
)
from ...chat.services.whatsapp_service import send_verification_message

user_router = APIRouter(
    tags=['Users']
)


@user_router.get('/', response_model=List[UserSchema])
async def user_list(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    db_users = await get_users(db)
    return db_users


@user_router.get('/me', response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user"""
    return current_user

@user_router.get("/me/info")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "whatsapp_number": current_user.whatsapp_number,
        "niche": current_user.niche,
        "is_active": current_user.is_active,
        "verification_status": current_user.verification_status,
        "whatsapp_lid": current_user.whatsapp_lid
    }

@user_router.patch("/me")
async def update_current_user(
    user_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    # Only allow updating specific fields
    allowed_fields = ["whatsapp_number", "niche", "username", "ai_tone", "broadcast_timing"]
    filtered_data = {k: v for k, v in user_data.items() if k in allowed_fields}
    
    updated_user = await update_user(db, current_user.id, filtered_data)
    return updated_user

@user_router.post("/me/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Manual trigger to resend the WhatsApp verification message"""
    if current_user.verification_status == "verified":
        return {"message": "User already verified"}
    
    if not current_user.whatsapp_number or current_user.whatsapp_number == "TBD":
        raise HTTPException(status_code=400, detail="No WhatsApp number configured")
        
    print(f"📩 Resending verification to {current_user.whatsapp_number}...")
    success = await send_verification_message(current_user.whatsapp_number)
    
    if not success:
        raise HTTPException(status_code=503, detail="WhatsApp service failed to send message")
        
    return {"message": "Verification message sent"}

@user_router.get('/{user_id}', response_model=UserSchema)
async def user_detail(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return db_user


@user_router.delete('/{user_id}')
async def user_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete user by ID"""
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    await delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@user_router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def user_create(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    # Check if user with email already exists
    existing_user = await get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await get_user_by_username(db, username=user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    new_user = await create_user(db, user)
    return new_user