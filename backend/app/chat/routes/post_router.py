# app/chat/routes/post_router.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import asyncio

from ...auth.services.auth_services import get_current_user
from ...core.database import get_db
from ..models.post import Post
from ...user.models.user import User
from ..services.agent_service import mcp_client
from ..tasks import publish_scheduled_post_task

post_router = APIRouter(tags=["posts"])

@post_router.get("/")
async def get_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get post history for current user"""
    result = await db.execute(
        select(Post).where(Post.user_id == current_user.id).order_by(Post.created_at.desc())
    )
    return result.scalars().all()

@post_router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated analytics for the dashboard"""
    result = await db.execute(
        select(Post).where(Post.user_id == current_user.id)
    )
    posts = result.scalars().all()
    
    from datetime import timedelta
    today = datetime.now().date()
    daily_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = len([p for p in posts if p.created_at.date() == day])
        daily_data.append({
            "name": day.strftime("%a"),
            "posts": count,
            "engagement": count * 15
        })
        
    return {
        "summary": {
            "total": len(posts),
            "facebook": len([p for p in posts if p.platform == 'facebook']),
            "instagram": len([p for p in posts if p.platform == 'instagram']),
            "scheduled": len([p for p in posts if p.status == 'scheduled'])
        },
        "trends": daily_data
    }

@post_router.post("/instant")
async def create_instant_post(
    post_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish a post immediately using parallel execution via asyncio.gather"""
    content = post_data.get("content")
    platform = post_data.get("platform")
    media_url = post_data.get("media_url")

    if not content or not platform:
        raise HTTPException(status_code=400, detail="Content and platform required")

    try:
        url_tool_map = {
            "facebook": "create_facebook_post",
            "instagram": "create_instagram_post"
        }

        platforms_to_post = [platform] if platform != "all" else ["facebook", "instagram"]
        
        async def deploy_one_platform(plat: str):
            tool_name = url_tool_map.get(plat)
            if not tool_name:
                return None
            
            # Platform constraints check
            if not media_url and plat == "instagram":
                return {"platform": plat, "result": {"success": False, "error": "Instagram requires a visual node (image/video)."}}
            
            start_time = datetime.now()
            try:
                # Direct tool invocation pattern for langchain-mcp-adapters 0.2+
                tools = await mcp_client.get_tools()
                target_tool = next((t for t in tools if t.name == tool_name), None)
                
                if not target_tool:
                    return {"platform": plat, "result": {"success": False, "error": f"Tool {tool_name} not found"}, "latency": 0}

                # Concurrent tool call
                tool_result = await target_tool.ainvoke({
                    "user_id": current_user.id,
                    "image_url": media_url,
                    "caption": content
                })

                import json
                # Robust parsing for list returns from MCP adapter
                if isinstance(tool_result, list):
                    text_content = next((c.text for c in tool_result if hasattr(c, "text")), None)
                    if not text_content:
                        text_content = next((str(c) for c in tool_result), None)
                    
                    try:
                        tool_result = json.loads(text_content) if text_content else {"success": False, "error": "Empty list response"}
                    except:
                        tool_result = {"success": True, "raw": text_content}

                latency = (datetime.now() - start_time).total_seconds() * 1000
                return {"platform": plat, "result": tool_result, "latency": latency}
            except Exception as e:
                return {"platform": plat, "result": {"success": False, "error": str(e)}, "latency": 0}

        # Execute all deployments in parallel
        tasks = [deploy_one_platform(p) for p in platforms_to_post]
        deploy_results = await asyncio.gather(*tasks)
        
        results_summary = []
        for dr in deploy_results:
            if not dr: continue
            
            plat = dr["platform"]
            tool_result = dr["result"]
            
            new_post = Post(
                user_id=current_user.id,
                content=content,
                media_url=media_url,
                platform=plat,
                status="published" if tool_result.get("success") else "failed",
                platform_post_id=str(tool_result.get("post_id", "") or tool_result.get("id", "")),
                meta_data=tool_result
            )
            db.add(new_post)
            results_summary.append({
                "platform": plat, 
                "success": tool_result.get("success"), 
                "latency": dr.get("latency", 0),
                "error": tool_result.get("error")
            })

        await db.commit()
        return {"success": True, "results": results_summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@post_router.post("/create")
async def schedule_post(
    post_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a post for later"""
    content = post_data.get("content")
    platform = post_data.get("platform")
    media_url = post_data.get("media_url")
    schedule_time = post_data.get("schedule_time")
    
    # Handle timezone-aware ISO format (convert to naive UTC for Celery if needed)
    final_schedule_time = None
    if schedule_time:
        dt = datetime.fromisoformat(schedule_time.replace("Z", "+00:00"))
        # Convert to UTC and then make naive for Celery
        import datetime as dt_module
        final_schedule_time = dt.astimezone(dt_module.timezone.utc).replace(tzinfo=None)

    new_post = Post(
        user_id=current_user.id,
        content=content,
        media_url=media_url,
        platform=platform,
        status="scheduled" if final_schedule_time else "published",
        schedule_time=final_schedule_time
    )
    db.add(new_post)
    await db.commit()

    # Enqueue in Celery if scheduled for later
    if new_post.status == "scheduled" and new_post.schedule_time:
        print(f"📅 [SCHEDULER] Post {new_post.id} enqueued for UTC: {new_post.schedule_time}")
        publish_scheduled_post_task.apply_async(
            args=[new_post.id],
            eta=new_post.schedule_time
        )
    else:
        print(f"🚀 [SCHEDULER] Post {new_post.id} has no schedule, saved as {new_post.status}")

    return {"success": True, "post": {
        "id": new_post.id,
        "status": new_post.status,
        "schedule_time": new_post.schedule_time.isoformat() if new_post.schedule_time else None
    }}

@post_router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a post from history"""
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == current_user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    await db.delete(post)
    await db.commit()
    return {"success": True, "message": "Post deleted"}
