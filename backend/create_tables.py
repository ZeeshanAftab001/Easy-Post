# create_tables.py
import asyncio
from app.core.database import engine, Base
from app.user.models.user import User
from app.oauth.models.social import SocialAccount
from app.chat.models.post import Post

async def create_tables():
    print("⏳ Creating tables...")
    async with engine.begin() as conn:
        # Create all tables defined in Base
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
