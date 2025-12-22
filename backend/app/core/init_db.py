# app/core/init_db.py
import asyncio
from sqlalchemy import text
from .database import engine, Base


async def init_db():
    print("Database URL configured for: localhost:5432/EasyPost")
    print("Initializing PostgreSQL database...")

    async with engine.begin() as conn:
        # Check which tables already exist
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        existing_tables = [row[0] for row in result]
        print(f"Existing tables: {existing_tables}")

        # Define tables you want
        required_tables = ['users', 'social_accounts', 'chat_sessions', 'chat_memories']
        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            print(f"Creating missing tables: {missing_tables}")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully!")
        else:
            print("✅ All tables already exist. No changes needed.")


if __name__ == "__main__":
    asyncio.run(init_db())