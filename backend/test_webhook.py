import asyncio
import httpx
import json

async def test_webhook():
    payload = {
        "event": "message",
        "session": "default",
        "payload": {
            "from": "923332112684@c.us",
            "to": "12345678@c.us",
            "body": "This is a test message to the AI agent!",
            "hasMedia": False
        }
    }
    
    print("Testing WhatsApp Webhook on local backend...")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post("http://localhost:8000/api/whatsapp/webhook", json=payload, timeout=60)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text}")
        except Exception as e:
            print(f"Failed to reach backend: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
