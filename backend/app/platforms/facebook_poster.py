# app/platforms/facebook_poster.py
import httpx
from app.core.config import settings

GRAPH_BASE = "https://graph.facebook.com"
API_VERSION = settings.FACEBOOK_GRAPH_VERSION


async def post_image_to_facebook(image_url: str = None, caption: str = "", page_id: str = "", page_token: str = "") -> dict:
    """Post to Facebook Page. Supports both images and text-only posts."""
    async with httpx.AsyncClient(timeout=60) as client:
        if image_url:
            # Image Post
            endpoint = f"{GRAPH_BASE}/{API_VERSION}/{page_id}/photos"
            payload = {"url": image_url, "caption": caption, "access_token": page_token, "published": "true"}
        else:
            # Text Post
            endpoint = f"{GRAPH_BASE}/{API_VERSION}/{page_id}/feed"
            payload = {"message": caption, "access_token": page_token}

        resp = await client.post(endpoint, data=payload)
        data = resp.json()
        
        if "error" in data:
            return {
                "success": False, 
                "platform": "facebook", 
                "error": data["error"].get("message"),
                "code": data["error"].get("code")
            }
            
        return {
            "success": True, 
            "platform": "facebook", 
            "post_id": data.get("post_id") or data.get("id"),
            "type": "visual" if image_url else "narrative"
        }