import asyncio
from sqlalchemy import text
from app.core.database import engine

async def force_sync_db():
    print("=== STARTING AGGRESSIVE DATABASE SYNC ===")
    async with engine.begin() as conn:
        # Check current columns
        result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        columns = [row[0] for row in result.fetchall()]
        print(f"Current columns detected: {columns}")
        
        needed_columns = {
            "ai_tone": "VARCHAR DEFAULT 'Professional'",
            "broadcast_timing": "VARCHAR DEFAULT 'Morning'"
        }
        
        for col, col_type in needed_columns.items():
            if col not in columns:
                print(f"Node Missing: {col}. Injecting now...")
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
            else:
                print(f"Node Active: {col}")
                
    print("=== DATABASE SYNC COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(force_sync_db())
