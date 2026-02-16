# test_connection.py

import asyncio
import logging
from app.mcp.instagram_client import get_instagram_client, get_facebook_page_info

logging.basicConfig(level=logging.INFO)

async def test():
    user_id = 2
    print(f"\n{'='*50}")
    print(f"Testing Instagram Connection for user {user_id}")
    print(f"{'='*50}\n")
    
    # First, check Facebook page info
    fb_info = await get_facebook_page_info(user_id)
    if fb_info:
        print(f"✅ Facebook Page Found:")
        print(f"   Name: {fb_info['page_name']}")
        print(f"   ID: {fb_info['page_id']}")
        print(f"   Token: {fb_info['token'][:50]}...")
    else:
        print("❌ No Facebook page found")
    
    # Then try to get Instagram client
    try:
        client, instagram_id = await get_instagram_client(user_id)
        print(f"\n✅ Instagram Client Created:")
        print(f"   Instagram ID: {instagram_id}")
        
        # Test profile
        profile = client.get_profile(instagram_id)
        if "error" not in profile:
            print(f"\n✅ Instagram Profile:")
            print(f"   Username: {profile.get('username')}")
            print(f"   Name: {profile.get('name')}")
            print(f"   Followers: {profile.get('followers_count', 0)}")
        else:
            print(f"\n❌ Profile Error: {profile['error']}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())