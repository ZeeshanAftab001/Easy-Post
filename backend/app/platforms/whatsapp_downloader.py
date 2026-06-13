# app/platforms/whatsapp_downloader.py
import httpx
import os
from app.core.config import settings

WAHA_URL = settings.WAHA_URL or "http://localhost:3000"

async def download_whatsapp_media(media_id: str) -> tuple[bytes, str]:
    """
    Download media from WAHA Node.
    Handles both direct URLs and Media IDs.
    """
    # If media_id is already a URL, use it directly
    if media_id and media_id.startswith("http"):
        url = media_id
    elif not media_id:
        raise ValueError("media_id or URL must be provided to download media")
    else:
        # Standard WAHA Files API path
        url = f"{WAHA_URL}/api/files/{media_id}"

    print(f"📥 Downloading media from: {url}")
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"❌ Download failed ({resp.status_code}): {url}")
                raise Exception(f"Could not retrieve media {url} (Status: {resp.status_code})")
            
            content = resp.content
            mime_type = resp.headers.get("content-type", "image/jpeg")
            
            print(f"✅ Downloaded {len(content)} bytes. MIME: {mime_type}")
            return content, mime_type
        except Exception as e:
            print(f"❌ Download Error: {e}")
            raise Exception(f"WhatsApp download error: {str(e)}")