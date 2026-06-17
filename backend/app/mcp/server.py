# app/mcp/server.py
import asyncio
import urllib.parse
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

from app.mcp.instagram_client import get_instagram_client
from app.mcp.facebook import FacebookClient
from app.mcp.platform_clients import (
    get_facebook_page_credentials,
)
from app.core.config import settings
from app.mcp.services.cloudinary_service import cloudinary_service

from app.platforms.whatsapp_downloader import download_whatsapp_media
from app.core.s3_service import s3_service
from app.platforms.validators import Platform, validate_for_platform, truncate_caption
from app.platforms.facebook_poster import post_image_to_facebook as _fb_post

from app.core.database import AsyncSessionLocal
from app.chat.models.post import Post
from app.core.celery_app import celery_app
import dateutil.parser



mcp = FastMCP("Easy-Post MCP")


# ============================================================================
# SHARED HELPER
# ============================================================================

async def _whatsapp_to_s3(media_id: str, user_id: int):
    """Download WhatsApp media and upload to S3. Returns (s3_url, bytes, mime) or error dict."""
    try:
        image_bytes, mime_type = await download_whatsapp_media(media_id)
    except Exception as e:
        return {"success": False, "error": f"WhatsApp download failed: {e}"}
    s3_url = await s3_service.upload_image(image_bytes, mime_type, folder=f"user_{user_id}/posts")
    if not s3_url:
        return {"success": False, "error": "S3 upload failed"}
    return s3_url, image_bytes, mime_type


async def _handle_scheduling(user_id: int, platform: str, media_url: str, caption: str, schedule_at: Optional[str]) -> Optional[dict]:
    """If schedule_at is provided, create a Post and return a success dict, else return None."""
    if not schedule_at:
        return None
    
    try:
        # Parse schedule_at (expecting ISO format or human-readable handled by dateutil)
        eta = dateutil.parser.parse(schedule_at)
        if eta.tzinfo is None:
            # Assume UTC if no timezone provided
            eta = eta.replace(tzinfo=None) # We'll let Celery handle it as UTC
        
        async with AsyncSessionLocal() as db:
            post = Post(
                user_id=user_id,
                content=caption,
                media_url=media_url,
                platform=platform,
                status="scheduled",
                schedule_time=eta
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            
            # Trigger Celery Task
            from app.chat.tasks import publish_scheduled_post_task
            publish_scheduled_post_task.apply_async(args=[post.id], eta=eta)
            
            return {
                "success": True, 
                "platform": platform, 
                "status": "scheduled", 
                "post_id": post.id, 
                "scheduled_for": eta.isoformat()
            }
    except Exception as e:
        return {"success": False, "error": f"Scheduling failed: {str(e)}"}


# ============================================================================
# CONNECTION & PROFILE
# ============================================================================

@mcp.tool()
async def verify_instagram_connection(user_id: int) -> dict:
    """Verify Instagram connection status."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        profile = client.get_profile(instagram_id)
        if "error" in profile:
            return {"success": False, "error": profile["error"].get("message")}
        return {"success": True, "message": "✅ Instagram connected",
                "username": profile.get("username"), "followers": profile.get("followers_count", 0),
                "posts": profile.get("media_count", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_instagram_profile(user_id: int) -> dict:
    """Get Instagram profile information."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        profile = client.get_profile(instagram_id)
        if "error" in profile:
            return {"success": False, "error": profile["error"].get("message")}
        return {"success": True, "username": profile.get("username"), "name": profile.get("name"),
                "followers": profile.get("followers_count", 0), "following": profile.get("follows_count", 0),
                "posts": profile.get("media_count", 0), "bio": profile.get("biography", ""),
                "website": profile.get("website", ""), "profile_picture": profile.get("profile_picture_url")}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# POSTS (read)
# ============================================================================

@mcp.tool()
async def get_instagram_posts(user_id: int, limit: int = 5) -> dict:
    """Get recent Instagram posts."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.get_posts(instagram_id, limit)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        posts = [{"id": p.get("id"), "caption": p.get("caption", "")[:100], "type": p.get("media_type"),
                  "media_url": p.get("media_url"), "likes": p.get("like_count", 0),
                  "comments": p.get("comments_count", 0), "url": p.get("permalink"), "timestamp": p.get("timestamp")}
                 for p in result.get("data", [])]
        return {"success": True, "posts": posts, "count": len(posts)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# INSIGHTS
# ============================================================================

@mcp.tool()
async def get_account_insights(user_id: int, days: int = 7) -> dict:
    """Get Instagram account insights for the last X days."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.get_insights(instagram_id, metrics="impressions,reach,profile_views", period="day")
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        insights = {}
        for metric in result.get("data", []):
            values = metric.get("values", [])
            if values:
                insights[metric.get("name")] = {
                    "total": sum(v.get("value", 0) for v in values),
                    "daily": [{"date": v.get("end_time"), "value": v.get("value")} for v in values]}
        return {"success": True, "period": f"Last {days} days", "insights": insights}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_post_insights(user_id: int, media_id: str) -> dict:
    """Get insights for a specific Instagram post."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_media_insights(media_id)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "media_id": media_id,
                "insights": {m.get("name"): m.get("values", [{}])[0].get("value", 0) for m in result.get("data", [])}}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_follower_growth(user_id: int, days: int = 7) -> dict:
    """Get follower count growth over time."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.get_insights(instagram_id, metrics="follower_count", period="day")
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        values = result.get("data", [{}])[0].get("values", [])
        start, end = (values[0].get("value", 0) if values else 0), (values[-1].get("value", 0) if values else 0)
        change = end - start
        return {"success": True, "current_followers": end,
                "growth": {"change": change, "percentage": round((change / start * 100), 2) if start > 0 else 0,
                           "daily": [{"date": v.get("end_time"), "followers": v.get("value")} for v in values]}}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# POST IMAGE — INSTAGRAM
# ============================================================================

@mcp.tool()
async def post_image_to_instagram(user_id: int, media_id: str, caption: str = "", schedule_at: Optional[str] = None) -> dict:
    """
    Post a WhatsApp image with caption to Instagram (or schedule it).

    Args:
        user_id:  Internal user ID — credentials fetched from DB automatically
        media_id: WAHA media_id (or url) from the incoming webhook
        caption:  Post caption (max 2,200 chars, auto-truncated)
        schedule_at: ISO format date string (e.g. "2024-07-01T10:00:00") to schedule via Celery.
    """
    result = await _whatsapp_to_s3(media_id, user_id)
    if isinstance(result, dict):
        return result
    s3_url, image_bytes, mime_type = result

    # If scheduling requested, handle and return early
    schedule_result = await _handle_scheduling(user_id, "instagram", s3_url, caption, schedule_at)
    if schedule_result:
        return schedule_result

    v = validate_for_platform(Platform.INSTAGRAM, image_bytes, mime_type, caption)
    if not v.valid:
        return {"success": False, "platform": "instagram", "errors": v.errors}
    cap = truncate_caption(caption, Platform.INSTAGRAM)
    try:
        client, instagram_id = await get_instagram_client(user_id)
        r = client.create_image_post(instagram_id, s3_url, cap)
        if "error" in r:
            return {"success": False, "platform": "instagram", "error": r["error"].get("message")}
        return {"success": True, "platform": "instagram", "post_id": r.get("id"), "image_url": s3_url}
    except Exception as e:
        return {"success": False, "platform": "instagram", "error": str(e)}


# ============================================================================
# FACEBOOK TOOLS
# ============================================================================

@mcp.tool()
async def get_facebook_page_info(user_id: int) -> dict:
    """Get basic information and follower count about the connected Facebook Page."""
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        client = FacebookClient(access_token=page_token, page_id=page_id)
        result = client.get_page_info()
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "page_info": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_facebook_recent_posts(user_id: int, limit: int = 10) -> dict:
    """Get recent posts from the Facebook Page feed."""
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        client = FacebookClient(access_token=page_token, page_id=page_id)
        result = client.get_recent_posts(limit=limit)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "posts": result.get("data", [])}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_facebook_page_analytics(user_id: int, period: str = "day") -> dict:
    """Get analytics (insights) for the Facebook Page."""
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        client = FacebookClient(access_token=page_token, page_id=page_id)
        result = client.get_page_analytics(period=period)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        insights = {}
        for metric in result.get("data", []):
            values = metric.get("values", [])
            if values:
                insights[metric.get("name")] = {
                    "daily": [{"date": v.get("end_time"), "value": v.get("value")} for v in values]
                }
        return {"success": True, "period": period, "insights": insights}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_facebook_text_post(user_id: int, message: str) -> dict:
    """Create a text-only post on the Facebook Page."""
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        client = FacebookClient(access_token=page_token, page_id=page_id)
        result = client.create_text_post(message)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "post_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def schedule_facebook_post(user_id: int, message: str, schedule_at: str) -> dict:
    """
    Schedule a text post for a future time on Facebook Page using Celery.
    
    Args:
        user_id: Internal user ID
        message: The text content of the post
        schedule_at: ISO format date string (e.g. "2024-07-01T10:00:00")
    """
    return await _handle_scheduling(user_id, "facebook", "", message, schedule_at)

# ============================================================================
# POST IMAGE — FACEBOOK
# ============================================================================

@mcp.tool()
async def post_image_to_facebook(user_id: int, media_id: str, caption: str, schedule_at: Optional[str] = None) -> dict:
    """
    Post a WhatsApp image with caption to the connected Facebook Page (or schedule it).

    Args:
        user_id:  Internal user ID — page credentials fetched from DB automatically
        media_id: WAHA media_id (or url) from the incoming webhook
        caption:  Post caption
        schedule_at: ISO format date string (e.g. "2024-07-01T10:00:00") to schedule via Celery.
    """
    result = await _whatsapp_to_s3(media_id, user_id)
    if isinstance(result, dict):
        return result
    s3_url, image_bytes, mime_type = result

    # If scheduling requested, handle and return early
    schedule_result = await _handle_scheduling(user_id, "facebook", s3_url, caption, schedule_at)
    if schedule_result:
        return schedule_result

    v = validate_for_platform(Platform.FACEBOOK, image_bytes, mime_type, caption)
    if not v.valid:
        return {"success": False, "platform": "facebook", "errors": v.errors}
    cap = truncate_caption(caption, Platform.FACEBOOK)
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        return await _fb_post(s3_url, cap, page_id, page_token)
    except Exception as e:
        return {"success": False, "platform": "facebook", "error": str(e)}



# ============================================================================
# POST IMAGE — ALL PLATFORMS
# ============================================================================

@mcp.tool()
async def post_image_to_all_platforms(user_id: int, media_id: str, caption: str, platforms: list[str], schedule_at: Optional[str] = None) -> dict:
    """
    Post a WhatsApp image to Meta platforms in one call (or schedule it).
    Image is downloaded once and uploaded to S3 once, then posted concurrently.

    Args:
        user_id:   Internal user ID
        media_id:  WAHA media_id (or url) from the incoming webhook
        caption:   Caption (auto-truncated per platform limits)
        platforms: e.g. ["instagram", "facebook"]
        schedule_at: ISO format date string (e.g. "2024-07-01T10:00:00") to schedule via Celery.
    """
    result = await _whatsapp_to_s3(media_id, user_id)
    if isinstance(result, dict):
        return {p: result for p in platforms}
    s3_url, image_bytes, mime_type = result

    # If scheduling requested, handle and return early
    # For "all platforms", we use "all" as the platform in DB
    schedule_result = await _handle_scheduling(user_id, "all", s3_url, caption, schedule_at)
    if schedule_result:
        return schedule_result

    async def _do_instagram():
        v = validate_for_platform(Platform.INSTAGRAM, image_bytes, mime_type, caption)
        if not v.valid:
            return {"success": False, "platform": "instagram", "errors": v.errors}
        cap = truncate_caption(caption, Platform.INSTAGRAM)
        try:
            client, ig_id = await get_instagram_client(user_id)
            r = client.create_image_post(ig_id, s3_url, cap)
            if "error" in r:
                return {"success": False, "platform": "instagram", "error": r["error"].get("message")}
            return {"success": True, "platform": "instagram", "post_id": r.get("id")}
        except Exception as e:
            return {"success": False, "platform": "instagram", "error": str(e)}

    async def _do_facebook():
        v = validate_for_platform(Platform.FACEBOOK, image_bytes, mime_type, caption)
        if not v.valid:
            return {"success": False, "platform": "facebook", "errors": v.errors}
        cap = truncate_caption(caption, Platform.FACEBOOK)
        try:
            page_id, page_token = await get_facebook_page_credentials(user_id)
            return await _fb_post(s3_url, cap, page_id, page_token)
        except Exception as e:
            return {"success": False, "platform": "facebook", "error": str(e)}

    fn_map = {"instagram": _do_instagram, "facebook": _do_facebook}
    valid_platforms = [p for p in platforms if p in fn_map]
    platform_results = await asyncio.gather(*[fn_map[p]() for p in valid_platforms])

    results = dict(zip(valid_platforms, platform_results))
    results["_meta"] = {"s3_url": s3_url, "mime_type": mime_type, "size_bytes": len(image_bytes)}
    return results


# ============================================================================
# LEGACY / URL-BASED TOOLS
# ============================================================================

@mcp.tool()
async def create_instagram_post(user_id: int, image_url: str, caption: str = "") -> dict:
    """Create an Instagram post from a direct image URL (not from WhatsApp)."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_image_post(instagram_id, image_url, caption)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "message": "✅ Post created", "post_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_facebook_post(user_id: int, image_url: str, caption: str) -> dict:
    """Create a Facebook Page post from an image URL."""
    try:
        page_id, page_token = await get_facebook_page_credentials(user_id)
        from app.platforms.facebook_poster import post_image_to_facebook as _fb_post
        return await _fb_post(image_url, caption, page_id, page_token)
    except Exception as e:
        return {"success": False, "error": str(e)}





@mcp.tool()
async def create_video_post(user_id: int, video_url: str, caption: str = "", cover_url: str = None) -> dict:
    """Create a new Instagram video post."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_video_post(instagram_id, video_url, caption, cover_url)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "message": "✅ Video post created", "post_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_carousel_post(user_id: int, media_urls: list, media_types: list, caption: str = "") -> dict:
    """Create a carousel post with multiple images/videos."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_carousel_post(instagram_id, media_urls, media_types, caption)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "message": "✅ Carousel post created", "post_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_text_post(user_id: int, text: str, background_color: str = "white", text_color: str = "black") -> dict:
    """Create a text-only Instagram post using Cloudinary."""
    if not settings.CLOUDINARY_CLOUD_NAME:
        return {"success": False, "error": "Cloudinary not configured"}
    try:
        encoded_text = urllib.parse.quote(text)
        cloudinary_url = (
            f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/"
            f"c_fill,w_1080,h_1080/b_rgb:{background_color.lstrip('#')}/"
            f"l_text:Arial_60:{encoded_text},co_rgb:{text_color.lstrip('#')},g_center/v1/instagram_post"
        )
        response = requests.get(cloudinary_url, timeout=30)
        if response.status_code != 200:
            return {"success": False, "error": "Failed to generate image"}
        image_url = await cloudinary_service.upload_image(response.content, folder=f"user_{user_id}/text_posts")
        if not image_url:
            return {"success": False, "error": "Failed to upload image"}
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_image_post(instagram_id, image_url, text)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "message": "✅ Text post created", "post_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_post_comments(user_id: int, media_id: str) -> dict:
    """Get comments on a specific post."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_comments(media_id)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "comments": result.get("data", [])}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def reply_to_comment(user_id: int, comment_id: str, message: str) -> dict:
    """Reply to a comment."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.reply_to_comment(comment_id, message)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "message": "✅ Reply posted", "reply_id": result.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def search_hashtag(user_id: int, hashtag: str) -> dict:
    """Search for a hashtag."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_hashtag_info(hashtag)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "hashtag": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_hashtag_media(user_id: int, hashtag: str, limit: int = 25) -> dict:
    """Get recent media for a hashtag."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_hashtag_media(hashtag, limit)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "hashtag": hashtag, "media": result.get("data", [])}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def check_media_status(user_id: int, container_id: str) -> dict:
    """Check the status of a media container."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_media_status(container_id)
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        return {"success": True, "container_id": container_id, "status": result.get("status_code", "UNKNOWN")}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def debug_database(user_id: int) -> dict:
    """Check database for troubleshooting."""
    from sqlalchemy import create_engine, text
    try:
        db_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
        engine = create_engine(db_url)
        with engine.connect() as conn:
            accounts = conn.execute(
                text("SELECT platform, is_active, pages IS NOT NULL as has_pages FROM social_accounts WHERE user_id = :uid"),
                {"uid": user_id},
            ).fetchall()
        return {"success": True, "accounts": [{"platform": a[0], "active": a[1], "has_pages": a[2]} for a in accounts]}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# MAIN
# ============================================================================

def main():
    mcp.run()


if __name__ == "__main__":
    main()