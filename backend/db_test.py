# test_db_connection.py

import asyncio
import json
from app.core.database import AsyncSessionLocal
from sqlalchemy import select, text
from app.oauth.models.social import SocialAccount

async def test_database():
    """Test database connection and data retrieval."""
    print("="*60)
    print("TESTING DATABASE CONNECTION")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        # Test 1: Check if we can connect
        try:
            result = await db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return
        
        # Test 2: Get all accounts for user 2
        user_id = 2
        result = await db.execute(
            select(SocialAccount).where(SocialAccount.user_id == user_id)
        )
        accounts = result.scalars().all()
        
        print(f"\nFound {len(accounts)} accounts for user {user_id}:")
        
        for acc in accounts:
            print(f"\n--- Account ID: {acc.id} ---")
            print(f"  Platform: {acc.platform}")
            print(f"  Platform User ID: {acc.platform_user_id}")
            print(f"  Is Active: {acc.is_active}")
            print(f"  Has Pages: {'Yes' if acc.pages else 'No'}")
            
            if acc.pages:
                try:
                    pages = json.loads(acc.pages)
                    print(f"  Pages data: {json.dumps(pages, indent=2)[:200]}...")
                except:
                    print(f"  Raw pages: {acc.pages[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_database())