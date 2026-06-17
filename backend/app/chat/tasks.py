# app/chat/tasks.py
import asyncio
import io
import fitz
from ..core.celery_app import celery_app
from .services.knowledge_service import store_user_knowledge
from .services.agent_service import mcp_client
from .models.post import Post
from ..core.database import AsyncSessionLocal
from sqlalchemy import select, func
from datetime import datetime

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

@celery_app.task(name="index_knowledge_file")
def index_knowledge_file_task(user_id: int, file_content: bytes, filename: str):
    """Background task to index a file into the vector database."""
    content = ""
    try:
        if filename.endswith(".pdf"):
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                content += page.get_text()
            doc.close()
        elif filename.endswith(".txt"):
            content = file_content.decode("utf-8")
        
        if not content.strip():
            return f"Error: File {filename} was empty."

        chunks = chunk_text(content)
        
        # We need to run the async database operations in the sync Celery worker
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # This shouldn't happen in a Celery worker but good to be safe
            future = asyncio.ensure_future(_store_chunks(user_id, chunks, filename))
            loop.run_until_complete(future)
        else:
            asyncio.run(_store_chunks(user_id, chunks, filename))

        return f"Successfully indexed {len(chunks)} chunks from {filename}"

    except Exception as e:
        return f"Failed to index {filename}: {str(e)}"

async def _store_chunks(user_id: int, chunks: list, filename: str):
    for chunk in chunks:
        await store_user_knowledge(
            user_id=user_id,
            category=f"file_{filename[:30]}",
            content=chunk
        )

@celery_app.task(name="publish_scheduled_post")
def publish_scheduled_post_task(post_id: int):
    """Background task to publish a scheduled post using Meta tools."""
    async def _publish():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from ..core.database import DATABASE_URL
        
        # New engine for each loop to avoid loop-closed errors on Windows
        local_engine = create_async_engine(DATABASE_URL)
        local_session = async_sessionmaker(local_engine, class_=AsyncSession, expire_on_commit=False)
        
        async with local_session() as db:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            
            if not post or post.status != "scheduled":
                await local_engine.dispose()
                return f"Post {post_id} not found or not in scheduled status."

            print(f"⏰ Celery: Publishing post {post.id} to {post.platform}")
            
            try:
                # Map platform to tools (support "all" platforms)
                platforms_to_deploy = [post.platform] if post.platform != "all" else ["facebook", "instagram"]
                url_tool_map = {
                    "facebook": "create_facebook_post",
                    "instagram": "create_instagram_post"
                }

                tools = await mcp_client.get_tools()
                
                results_summary = []
                success_count = 0
                
                for plat in platforms_to_deploy:
                    # Decide tool based on content
                    if plat == "facebook" and not post.media_url:
                        tool_name = "create_facebook_text_post"
                        tool_args = {"user_id": post.user_id, "message": post.content}
                    else:
                        tool_name = url_tool_map.get(plat)
                        tool_args = {
                            "user_id": post.user_id,
                            "image_url": post.media_url or "", # Ensure not None
                            "caption": post.content
                        }

                    if not tool_name: continue

                    target_tool = next((t for t in tools if t.name == tool_name), None)
                    if not target_tool:
                        results_summary.append({"platform": plat, "error": f"Tool {tool_name} not found"})
                        continue

                    print(f"📡 Worker: Deploying to {plat} via {tool_name}...")
                    tool_result = await target_tool.ainvoke(tool_args)

                    import json
                    # Robust parsing
                    if isinstance(tool_result, list):
                        text_content = next((c.text for c in tool_result if hasattr(c, "text")), None)
                        if not text_content: text_content = next((str(c) for c in tool_result), None)
                        try:
                            tool_result = json.loads(text_content) if text_content else {"success": False, "error": "Empty response"}
                        except:
                            tool_result = {"success": True, "raw": text_content}

                    if tool_result.get("success"):
                        success_count += 1
                        if not post.platform_post_id: # Save first success ID
                            post.platform_post_id = str(tool_result.get("post_id") or tool_result.get("id", ""))
                    
                    results_summary.append({"platform": plat, "result": tool_result})

                # Final status determination
                if success_count == len(platforms_to_deploy):
                    post.status = "published"
                elif success_count > 0:
                    post.status = "published" # Partial success is still published
                else:
                    post.status = "failed"
                
                post.meta_data = {"deployment_log": results_summary}
                await db.commit()
                await local_engine.dispose()
                return f"Post {post_id} finished with status: {post.status}"

            except Exception as e:
                if 'post' in locals() and post:
                    post.status = "failed"
                    post.meta_data = {"error": str(e)}
                    await db.commit()
                await local_engine.dispose()
                return f"Error publishing post {post_id}: {str(e)}"

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(_publish())
        else:
            return asyncio.run(_publish())
    except RuntimeError:
        return asyncio.run(_publish())

@celery_app.task(name="sync_social_feed")
def sync_social_feed_task(user_id: int):
    """Sync existing posts from Meta platforms to Content Hub."""
    from ..oauth.models.social import SocialAccount
    import json

    async def _sync():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from ..core.database import DATABASE_URL
        
        local_engine = create_async_engine(DATABASE_URL)
        local_session = async_sessionmaker(local_engine, class_=AsyncSession, expire_on_commit=False)

        async with local_session() as db:
            print(f"🔄 Celery: Syncing social feed for user {user_id}")
            # Get linked accounts
            result = await db.execute(
                select(SocialAccount).where(SocialAccount.user_id == user_id)
            )
            accounts = result.scalars().all()
            
            if not accounts:
                await local_engine.dispose()
                return "No linked accounts found."

            tools = await mcp_client.get_tools()
            
            total_synced = 0
            for account in accounts:
                tool_name = {
                    "facebook": "get_facebook_recent_posts",
                    "instagram": "get_instagram_posts"
                }.get(account.platform)

                if not tool_name:
                    continue

                target_tool = next((t for t in tools if t.name == tool_name), None)
                if not target_tool:
                    print(f"⚠️ Tool {tool_name} not found")
                    continue

                print(f"📡 Pulling {account.platform} posts...")
                try:
                    tool_result = await target_tool.ainvoke({"user_id": user_id})
                    
                    # Tool returns a JSON string usually
                    if isinstance(tool_result, str):
                        data = json.loads(tool_result)
                    else:
                        data = tool_result

                    posts_data = data.get("posts", [])

                    for p_data in posts_data:
                        # Extract platform ID
                        p_id = str(p_data.get("id"))
                        
                        # Check exist
                        exist_check = await db.execute(
                            select(Post).where(Post.platform_post_id == p_id)
                        )
                        if exist_check.scalar_one_or_none():
                            continue

                        # Create new post record
                        new_post = Post(
                            user_id=user_id,
                            content=p_data.get("caption") or p_data.get("message") or "No content",
                            media_url=p_data.get("media_url") or p_data.get("full_picture"),
                            platform=account.platform,
                            status="published",
                            platform_post_id=p_id,
                            meta_data=p_data,
                            # Try to parse timestamp
                            created_at=datetime.fromisoformat(p_data["timestamp"].replace("Z", "+00:00")) if "timestamp" in p_data else func.now()
                        )
                        db.add(new_post)
                        total_synced += 1

                except Exception as e:
                    print(f"❌ Error syncing {account.platform}: {str(e)}")

            await db.commit()
            await local_engine.dispose()
            return f"Synced {total_synced} new posts for user {user_id}"

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.run_until_complete(_sync())
        else:
            return asyncio.run(_sync())
    except RuntimeError:
        return asyncio.run(_sync())
