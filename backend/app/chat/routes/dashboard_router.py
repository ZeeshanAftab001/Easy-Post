from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import time

from ...auth.services.auth_services import get_current_active_user
from ...core.database import get_db
from ...user.models.user import User
from ...oauth.models.social import SocialAccount
from ...chat.models.post import Post
from ...oauth.services.social_service import SocialAccountService

dashboard_router = APIRouter(tags=["Dashboard"])
social_service = SocialAccountService()

@dashboard_router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Optimized consolidated dashboard endpoint.
    Uses SQL aggregation to avoid fetching large datasets into memory.
    """
    start_time = time.time()
    
    # 1. User Info (Fast)
    user_info = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "subscription_tier": getattr(current_user, 'subscription_tier', 'System Admin'),
        "is_active": current_user.is_active
    }
    
    # 2. Fetch Linked Accounts (Fast)
    accounts = await social_service.get_user_social_accounts(db, current_user.id)
    account_fetch_time = time.time()
    
    # 3. Optimized Analytics Queries (SQL Level)
    # Total count
    total_result = await db.execute(
        select(func.count(Post.id)).where(Post.user_id == current_user.id)
    )
    total_posts = total_result.scalar() or 0
    
    # Platform counts
    platform_counts_result = await db.execute(
        select(Post.platform, func.count(Post.id))
        .where(Post.user_id == current_user.id)
        .group_by(Post.platform)
    )
    platform_counts = dict(platform_counts_result.all())
    
    # Status counts (e.g., scheduled)
    scheduled_result = await db.execute(
        select(func.count(Post.id))
        .where(Post.user_id == current_user.id, Post.status == 'scheduled')
    )
    scheduled_posts = scheduled_result.scalar() or 0
    
    # Trend data (Last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    trend_result = await db.execute(
        select(func.date(Post.created_at), func.count(Post.id))
        .where(Post.user_id == current_user.id, Post.created_at >= seven_days_ago)
        .group_by(func.date(Post.created_at))
    )
    trend_map = {str(d): c for d, c in trend_result.all()}
    
    today = datetime.now().date()
    daily_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = str(day)
        count = trend_map.get(day_str, 0)
        daily_data.append({
            "name": day.strftime("%a"),
            "posts": count,
            "engagement": count * 15
        })
    
    analytics_time = time.time()
    
    # PERFORMANCE DIAGNOSTIC
    total_latency = (analytics_time - start_time) * 1000
    print(f"⏱️ [DASHBOARD] Accounts: {(account_fetch_time - start_time)*1000:.2f}ms | Analytics: {(analytics_time - account_fetch_time)*1000:.2f}ms | Total: {total_latency:.2f}ms")
    
    return {
        "user": user_info,
        "accounts": accounts,
        "analytics": {
            "summary": {
                "total": total_posts,
                "facebook": platform_counts.get('facebook', 0),
                "instagram": platform_counts.get('instagram', 0),
                "scheduled": scheduled_posts
            },
            "trends": daily_data
        }
    }
