import asyncio
import json
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.oauth.models.social import SocialAccount

async def debug_pages():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(SocialAccount).where(SocialAccount.user_id == 1))
        accounts = result.scalars().all()
        
        print(f"--- DEEP DEBUG: PAGE TOKENS FOR USER 1 ---")
        for acc in accounts:
            print(f"Platform: {acc.platform}")
            if acc.pages:
                try:
                    pages = json.loads(acc.pages)
                    print(f"Found {len(pages)} pages.")
                    for p in pages:
                        p_name = p.get('name')
                        p_id = p.get('id')
                        p_token = p.get('access_token')
                        has_token = "YES" if p_token else "NO"
                        # Only show tip of token for safety
                        token_preview = f"{p_token[:10]}..." if p_token else "None"
                        print(f"  - Page: {p_name} ({p_id}) | Token Stored: {has_token} ({token_preview})")
                except Exception as e:
                    print(f"  - Error parsing pages JSON: {e}")
            else:
                print("  - No pages JSON found.")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(debug_pages())
