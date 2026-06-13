import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.oauth.models.social import SocialAccount

async def debug_tokens():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SocialAccount).where(SocialAccount.user_id == 1))
        accounts = result.scalars().all()
        
        print(f"--- DEBUG: DATA FOR USER 1 ---")
        if not accounts:
            print("❌ No social accounts found for User 1 in DB.")
            return
            
        for acc in accounts:
            print(f"Platform: {acc.platform}")
            print(f"Active: {acc.is_active}")
            print(f"Has Pages: {bool(acc.pages)}")
            print(f"Expires: {acc.token_expires_at}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(debug_tokens())
