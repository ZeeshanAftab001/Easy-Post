import asyncio
import httpx
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.config import settings

async def setup_webhook():
    print(f"Setting up Webhook for WAHA at {settings.WAHA_URL}")
    print(f"Backend URL target: {settings.BACKEND_URL}/api/whatsapp/webhook")
    
    # Check if we should use HTTP header for WAHA auth
    headers = {}
    if settings.WAHA_API_KEY:
        headers["X-Api-Key"] = settings.WAHA_API_KEY
    
    # This endpoint configures webhooks for WAHA Plus/Core dynamically 
    url = f"{settings.WAHA_URL}/api/sessions/{settings.WAHA_SESSION}/config"
    payload = {
        "webhooks": [
            {
                "url": f"{settings.BACKEND_URL}/api/whatsapp/webhook",
                "events": ["message", "message.any"]
            }
        ]
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        try:
            r = await client.put(
                url, 
                json=payload, 
                timeout=30
                # Note: some WAHA versions use PUT or POST. We try PUT first and then POST if it fails.
            )
            
            if r.status_code == 404:
                # Fallback for older WAHA endpoints
                print("PUT /config failed with 404, trying POST /webhooks instead or similar...")
                
            r.raise_for_status()
            print("✅ Webhook configured successfully in WAHA!")
            print(f"WAHA will now forward messages to: {settings.BACKEND_URL}/api/whatsapp/webhook")
        except Exception as e:
            print(f"❌ Failed to set webhook via API: {e}")
            if hasattr(e, 'response') and e.response:
                print(e.response.text)
            
            print("\n⚠️ Alternative Method:")
            print("If dynamic webhooks aren't supported by your version of WAHA, you can:")
            print("1. Go to http://localhost:3000/dashboard/")
            print("2. Find the Webhooks section and manually input your URL:")
            print(f"   {settings.BACKEND_URL}/api/whatsapp/webhook")

if __name__ == "__main__":
    asyncio.run(setup_webhook())
