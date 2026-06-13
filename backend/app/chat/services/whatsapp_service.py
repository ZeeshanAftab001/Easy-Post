import requests
import os
import httpx
from ...core.config import settings

WAHA_URL = settings.WAHA_URL
WAHA_SESSION = settings.WAHA_SESSION
WAHA_API_KEY = settings.WAHA_API_KEY

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)


# ======================== #
#         SEND TEXT        #
# ======================== #
async def send_text(to: str, text: str):
    """
    Send text via WAHA /api/sendText
    """
    url = f"{WAHA_URL}/api/sendText"
    
    # Handle both plain numbers and full JIDs
    chat_id = to if "@" in to else f"{to}@c.us"
    
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": WAHA_SESSION
    }
    
    headers = {}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY

    async with httpx.AsyncClient(headers=headers) as client:
        try:
            r = await client.post(url, json=payload, timeout=30)
            r.raise_for_status()
            print(f"✅ WAHA Text Sent to {chat_id}: {r.status_code}")
            return r.json()
        except Exception as e:
            print(f"❌ WAHA sendText Failed: {e}")
            return None


# ======================== #
#         SEND FILE        #
# ======================== #
async def send_file(to: str, file_url: str, caption: str = ""):
    """
    Send media/file via WAHA /api/sendFile
    Works for images, audio, video.
    """
    url = f"{WAHA_URL}/api/sendFile"
    
    # Handle both plain numbers and full JIDs
    chat_id = to if "@" in to else f"{to}@c.us"
    
    payload = {
        "chatId": chat_id,
        "file": {
            "url": file_url
        },
        "caption": caption,
        "session": WAHA_SESSION
    }
    
    headers = {}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY

    async with httpx.AsyncClient(headers=headers) as client:
        try:
            r = await client.post(url, json=payload, timeout=45)
            r.raise_for_status()
            print(f"✅ WAHA File Sent to {to}: {r.status_code}")
            return r.json()
        except Exception as e:
            print(f"❌ WAHA sendFile Failed: {e}")
            return None


# ======================== #
#         VERIFICATION      #
# ======================== #
async def send_verification_message(to: str):
    """
    Send the initial verification message to a new user.
    """
    text = (
        "Welcome to Easy-Post! 🚀\n\n"
        "To verify your phone number and link your account, please reply to this message with exactly: *DONE*"
    )
    return await send_text(to, text)
