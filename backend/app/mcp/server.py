# app/mcp/server.py
import urllib.parse
import requests
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from app.mcp.instagram_client import get_instagram_client
from app.core.config import settings
from app.mcp.services.cloudinary_service import cloudinary_service


mcp = FastMCP("Instagram MCP")


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
        
        return {
            "success": True,
            "message": "✅ Instagram connected",
            "username": profile.get("username"),
            "followers": profile.get("followers_count", 0),
            "posts": profile.get("media_count", 0)
        }
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
        
        return {
            "success": True,
            "username": profile.get("username"),
            "name": profile.get("name"),
            "followers": profile.get("followers_count", 0),
            "following": profile.get("follows_count", 0),
            "posts": profile.get("media_count", 0),
            "bio": profile.get("biography", ""),
            "website": profile.get("website", ""),
            "profile_picture": profile.get("profile_picture_url")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# POSTS
# ============================================================================

@mcp.tool()
async def get_instagram_posts(user_id: int, limit: int = 5) -> dict:
    """Get recent Instagram posts."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.get_posts(instagram_id, limit)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        posts = []
        for post in result.get("data", []):
            posts.append({
                "id": post.get("id"),
                "caption": post.get("caption", "")[:100],
                "type": post.get("media_type"),
                "media_url": post.get("media_url"),
                "likes": post.get("like_count", 0),
                "comments": post.get("comments_count", 0),
                "url": post.get("permalink"),
                "timestamp": post.get("timestamp")
            })
        
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
        
        # Calculate date range
        since = (datetime.now() - timedelta(days=min(days, 30))).strftime("%Y-%m-%d")
        until = datetime.now().strftime("%Y-%m-%d")
        
        # Use the client's get_insights method
        result = client.get_insights(
            instagram_id, 
            metrics="impressions,reach,profile_views",
            period="day"
        )
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        # Format the response
        insights = {}
        for metric in result.get("data", []):
            name = metric.get("name")
            values = metric.get("values", [])
            if values:
                insights[name] = {
                    "total": sum(v.get("value", 0) for v in values),
                    "daily": [{"date": v.get("end_time"), "value": v.get("value")} for v in values]
                }
        
        return {
            "success": True,
            "period": f"Last {days} days",
            "insights": insights
        }
        
    except Exception as e:
       
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_post_insights(user_id: int, media_id: str) -> dict:
    """Get insights for a specific post."""
    try:
        client, _ = await get_instagram_client(user_id)
        
        result = client.get_media_insights(media_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        insights = {}
        for metric in result.get("data", []):
            insights[metric.get("name")] = metric.get("values", [{}])[0].get("value", 0)
        
        return {
            "success": True,
            "media_id": media_id,
            "insights": insights
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_follower_growth(user_id: int, days: int = 7) -> dict:
    """Get follower count growth over time."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        
        result = client.get_insights(
            instagram_id,
            metrics="follower_count",
            period="day"
        )
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        values = result.get("data", [{}])[0].get("values", [])
        growth = [{"date": v.get("end_time"), "followers": v.get("value")} for v in values]
        
        start = values[0].get("value", 0) if values else 0
        end = values[-1].get("value", 0) if values else 0
        change = end - start
        
        return {
            "success": True,
            "current_followers": end,
            "growth": {
                "change": change,
                "percentage": round((change / start * 100), 2) if start > 0 else 0,
                "daily": growth
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# CREATE POSTS
# ============================================================================

@mcp.tool()
async def create_instagram_post(user_id: int, image_url: str, caption: str = "") -> dict:
    """Create a new Instagram post with an image."""
    try:
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_image_post(instagram_id, image_url, caption)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        return {
            "success": True,
            "message": "✅ Post created",
            "post_id": result.get("id")
        }
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
        
        return {
            "success": True,
            "message": "✅ Video post created",
            "post_id": result.get("id")
        }
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
        
        return {
            "success": True,
            "message": "✅ Carousel post created",
            "post_id": result.get("id")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# TEXT-ONLY POST (using Cloudinary)
# ============================================================================

@mcp.tool()
async def create_text_post(user_id: int, text: str, background_color: str = "white", text_color: str = "black") -> dict:
    """Create a text-only Instagram post using Cloudinary."""
    
    if not settings.CLOUDINARY_CLOUD_NAME:
        return {"success": False, "error": "Cloudinary not configured"}
    
    try:
        # Generate image with text using Cloudinary
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        encoded_text = urllib.parse.quote(text)
        
        cloudinary_url = (
            f"https://res.cloudinary.com/{cloud_name}/image/upload/"
            f"c_fill,w_1080,h_1080/"
            f"b_rgb:{background_color.lstrip('#')}/"
            f"l_text:Arial_60:{encoded_text},co_rgb:{text_color.lstrip('#')},g_center/"
            f"v1/instagram_post"
        )
        
        # Download and upload to Cloudinary
        response = requests.get(cloudinary_url, timeout=30)
        if response.status_code != 200:
            return {"success": False, "error": "Failed to generate image"}
        
        image_url = await cloudinary_service.upload_image(
            response.content,
            folder=f"user_{user_id}/text_posts"
        )
        
        if not image_url:
            return {"success": False, "error": "Failed to upload image"}
        
        # Post to Instagram using the client
        client, instagram_id = await get_instagram_client(user_id)
        result = client.create_image_post(instagram_id, image_url, text)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        return {
            "success": True,
            "message": "✅ Text post created",
            "post_id": result.get("id")
        }
    except Exception as e:
     
        return {"success": False, "error": str(e)}


# ============================================================================
# COMMENTS
# ============================================================================

@mcp.tool()
async def get_post_comments(user_id: int, media_id: str) -> dict:
    """Get comments on a specific post."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_comments(media_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        return {
            "success": True,
            "comments": result.get("data", [])
        }
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
        
        return {
            "success": True,
            "message": "✅ Reply posted",
            "reply_id": result.get("id")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# HASHTAGS
# ============================================================================

@mcp.tool()
async def search_hashtag(user_id: int, hashtag: str) -> dict:
    """Search for a hashtag and get its ID."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_hashtag_info(hashtag)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        return {
            "success": True,
            "hashtag": result
        }
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
        
        return {
            "success": True,
            "hashtag": hashtag,
            "media": result.get("data", [])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# MEDIA STATUS
# ============================================================================

@mcp.tool()
async def check_media_status(user_id: int, container_id: str) -> dict:
    """Check the status of a media container (for video processing)."""
    try:
        client, _ = await get_instagram_client(user_id)
        result = client.get_media_status(container_id)
        
        if "error" in result:
            return {"success": False, "error": result["error"].get("message")}
        
        return {
            "success": True,
            "container_id": container_id,
            "status": result.get("status_code", "UNKNOWN"),
            "details": result.get("status", "No details")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# DEBUG
# ============================================================================

@mcp.tool()
async def debug_database(user_id: int) -> dict:
    """Check database for troubleshooting."""
    from sqlalchemy import create_engine, text
    
    try:
        db_url = settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            accounts = conn.execute(
                text("""
                    SELECT platform, is_active, 
                           pages IS NOT NULL as has_pages
                    FROM social_accounts 
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchall()
        
        return {
            "success": True,
            "accounts": [{"platform": a[0], "active": a[1], "has_pages": a[2]} for a in accounts]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Log to stderr only - NEVER to stdout

    mcp.run()

if __name__ == "__main__":
    main()