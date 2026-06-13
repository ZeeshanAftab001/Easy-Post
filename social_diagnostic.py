
import asyncio
import sys
import os
from sqlalchemy import select

# Setup path so we can import from backend
os.chdir('backend')
sys.path.append(os.getcwd())
os.environ['PYTHONPATH'] = os.getcwd()

from app.core.database import AsyncSessionLocal
from app.user.models.user import User
from app.chat.models.post import Post  # Required for relationships
from app.oauth.models.social import SocialAccount  # Required for relationships
from app.chat.services.agent_service import mcp_client

async def run_diagnostics():
    print("🚀 Starting Social Media Diagnostics...\n")
    
    async with AsyncSessionLocal() as db:
        # Find a user with social accounts
        # We'll just pick the first one we find for testing
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("❌ No users found in database.")
            return

        print(f"🔍 Found {len(users)} users. Testing tokens for the current environment...")
        
        # Initialize MCP Tools
        print("🔗 Connecting to MCP Server...")
        tools = await mcp_client.get_tools()
        
        def get_tool(name):
            return next((t for t in tools if t.name == name), None)

        fb_info_tool = get_tool("get_facebook_page_info")
        ig_verify_tool = get_tool("verify_instagram_connection")

        for user in users:
            print(f"\n👤 Testing for User: {user.username} (ID: {user.id})")
            
            async def _safe_invoke(tool, args):
                try:
                    res = await tool.ainvoke(args)
                    # Handle LangChain tool return format (list of content objects)
                    if isinstance(res, list) and len(res) > 0:
                        import json
                        raw_text = getattr(res[0], 'text', str(res[0]))
                        try:
                            # Try parsing if it's a JSON string
                            return json.loads(raw_text)
                        except:
                            return {"success": False, "error": raw_text}
                    return res
                except Exception as e:
                    return {"success": False, "error": str(e)}

            # --- FACEBOOK ---
            if fb_info_tool:
                print("  🔹 Checking Facebook...")
                fb_res = await _safe_invoke(fb_info_tool, {"user_id": user.id})
                if fb_res.get("success"):
                    page = fb_res.get("page_info", {})
                    print(f"    ✅ Facebook: Connected to Page '{page.get('name')}'")
                    print(f"       Page ID: {page.get('id')}")
                    print(f"       Followers: {page.get('followers_count')}")
                else:
                    print(f"    ❌ Facebook: Failed - {fb_res.get('error', 'Unknown error')}")

            # --- INSTAGRAM ---
            if ig_verify_tool:
                print("  🔹 Checking Instagram...")
                ig_res = await _safe_invoke(ig_verify_tool, {"user_id": user.id})
                if ig_res.get("success"):
                    print(f"    ✅ Instagram: Connected as '{ig_res.get('username')}'")
                    print(f"       Followers: {ig_res.get('followers')}")
                else:
                    print(f"    ❌ Instagram: Failed - {ig_res.get('error', 'Unknown error')}")

    print("\n🏁 Diagnostics Complete.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
