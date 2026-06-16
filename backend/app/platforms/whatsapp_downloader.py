# app/platforms/whatsapp_downloader.py
import httpx
from app.core.config import settings

WAHA_URL = settings.WAHA_URL or "http://localhost:3000"

async def download_whatsapp_media(media_id: str) -> tuple[bytes, str]:
    """
    Download media from WAHA Node with authentication.
    Tries multiple authentication methods.
    """
    # Construct URL
    if media_id and media_id.startswith("http"):
        url = media_id
    elif not media_id:
        raise ValueError("media_id or URL must be provided to download media")
    else:
        url = f"{WAHA_URL}/api/files/{media_id}"

    print(f"📥 Downloading media from: {url}")
    
    # ── Try different authentication methods ──────────────────────────────
    auth_methods = []
    
    # Method 1: X-Api-Key header (most common)
    if settings.WAHA_API_KEY:
        auth_methods.append({
            "name": "X-Api-Key",
            "headers": {"X-Api-Key": settings.WAHA_API_KEY}
        })
        
        # Method 2: Authorization Bearer
        auth_methods.append({
            "name": "Bearer Token",
            "headers": {"Authorization": f"Bearer {settings.WAHA_API_KEY}"}
        })
    
    # Method 3: No authentication (fallback)
    auth_methods.append({
        "name": "No Auth",
        "headers": {}
    })
    
    last_error = None
    
    for method in auth_methods:
        try:
            print(f"🔑 Trying auth: {method['name']}")
            async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
                resp = await client.get(url, headers=method["headers"])
                
                if resp.status_code == 200:
                    content = resp.content
                    mime_type = resp.headers.get("content-type", "image/jpeg")
                    print(f"✅ Downloaded {len(content)} bytes using {method['name']}")
                    print(f"   MIME: {mime_type}")
                    return content, mime_type
                elif resp.status_code == 401:
                    print(f"⚠️ Auth method '{method['name']}' failed with 401")
                    last_error = f"Authentication failed with {method['name']}"
                else:
                    print(f"⚠️ Auth method '{method['name']}' failed with {resp.status_code}")
                    last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
        except Exception as e:
            print(f"⚠️ Auth method '{method['name']}' error: {e}")
            last_error = str(e)
    
    # If we get here, all methods failed
    raise Exception(f"WhatsApp download error: All authentication methods failed. Last error: {last_error}")