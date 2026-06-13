
from sqlalchemy import text
from app.core.database import engine
import asyncio

async def debug_db():
    async with engine.begin() as conn:
        # Check all users first
        users_res = await conn.execute(text("SELECT id, username FROM users"))
        users = users_res.fetchall()
        print(f"Users in DB: {users}")

        # Check memory
        res = await conn.execute(text("SELECT id, user_id, agent_kind, content, created_at FROM ai_agent_memory LIMIT 20"))
        rows = res.fetchall()
        print(f"\nMemory Rows (Total: {len(rows)}):")
        for r in rows:
            print(f"User: {r[1]} | Kind: {r[2]} | Content: {r[3][:50]}... | Created: {r[4]}")

if __name__ == "__main__":
    asyncio.run(debug_db())
