"""
One-time script to update your whatsapp_number in the DB.
WAHA sends your number as a LID (255799712591939) instead of your real phone number.
Run: python fix_whatsapp_number.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.user.models.user import User
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    async with async_session() as db:
        # Show all users and their whatsapp numbers
        result = await db.execute(select(User.id, User.email, User.username, User.whatsapp_number))
        users = result.all()
        
        print("\n--- Current Users in DB ---")
        for u in users:
            print(f"  ID={u.id} | Email={u.email} | Username={u.username} | WhatsApp={u.whatsapp_number}")
        
        if not users:
            print("No users found in DB.")
            return
        
        print("\nEnter the User ID to update (or press Enter to skip):")
        user_id = input("> ").strip()
        if not user_id:
            print("Skipped.")
            return
        
        print(f"Enter the NEW whatsapp_number for user ID {user_id}:")
        print("(The LID WAHA is sending is: 255799712591939)")
        new_number = input("> ").strip()
        if not new_number:
            print("Skipped.")
            return
        
        await db.execute(
            update(User).where(User.id == int(user_id)).values(whatsapp_number=new_number)
        )
        await db.commit()
        print(f"\n✅ Updated User ID={user_id} whatsapp_number → '{new_number}'")
        print("You can now send a WhatsApp message and the agent will recognize you!")

asyncio.run(main())
