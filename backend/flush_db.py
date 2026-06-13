import asyncio
from sqlalchemy import text
from app.core.database import engine

async def drop_all():
    print("WARNING: Starting Full Database Purge...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        print("Database Nodes Purged.")

if __name__ == "__main__":
    asyncio.run(drop_all())
