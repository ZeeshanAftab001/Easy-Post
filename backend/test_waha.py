import asyncio
import os
import sys

# Add the project root to sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.chat.services.whatsapp_service import send_text
from app.core.config import settings
import httpx

async def main():
    print(f"Testing WAHA server at: {settings.WAHA_URL}")
    print(f"Using Session: {settings.WAHA_SESSION}")
    
    # 1. Check if WAHA is running and get session status
    try:
        headers = {}
        if settings.WAHA_API_KEY:
            headers["X-Api-Key"] = settings.WAHA_API_KEY
            print("Using API Key from settings...")

        async with httpx.AsyncClient(headers=headers) as client:
            resp = await client.get(f"{settings.WAHA_URL}/api/sessions", params={"all": True})
            resp.raise_for_status()
            sessions = resp.json()
            print("\n--- WAHA Sessions ---")
            
            if isinstance(sessions, list):
                our_session = None
                for s in sessions:
                    name = s.get('name')
                    status = s.get('status')
                    print(f"Name: {name}, Status: {status}")
                    if name == settings.WAHA_SESSION:
                        our_session = s
                
                if not our_session:
                    print(f"\n⚠️ Session '{settings.WAHA_SESSION}' not found.")
                    print(f"Visit {settings.WAHA_URL}/dashboard to configure and start your session.")
                elif our_session.get('status') != 'WORKING':
                    print(f"\n⚠️ Session '{settings.WAHA_SESSION}' is not WORKING (Status: {our_session.get('status')}).")
                    print(f"Make sure to scan the QR code at {settings.WAHA_URL}/dashboard")
                else:
                    print("\n✅ Session is WORKING!")
            else:
                print(f"Unexpected response format: {sessions}")
                
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Error connecting to WAHA server: {e}")
        print(f"Response text: {e.response.text}")
        print(f"Response headers: {e.response.headers}")
        print("Make sure your docker container is up and running on port 3000.")
        return
    except Exception as e:
        print(f"\n❌ Error connecting to WAHA server: {e}")
        print("Make sure your docker container is up and running on port 3000.")
        return

    # 2. Check if a phone argument is passed to send text
    if len(sys.argv) > 1:
        phone = sys.argv[1]
        print(f"\nSending test message to {phone}...")
        result = await send_text(phone, "Hello! This is a test message from Easy-Post WAHA integration.")
        if result:
            print("\n✅ Message sent successfully!")
            print(result)
        else:
            print("\n❌ Failed to send message.")
    else:
        print("\nNote: To send a test message, run the script with a phone number (with country code, no '+', eg. 923...):")
        print("python test_waha.py <phone-number>")

if __name__ == "__main__":
    asyncio.run(main())
