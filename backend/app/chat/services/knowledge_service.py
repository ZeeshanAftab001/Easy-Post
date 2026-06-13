# app/chat/services/knowledge_service.py
#
# General user knowledge base (RAG) using pgvector and Redis caching.
# This stores brand guidelines, target audience info, and user preferences.

import uuid
import json
import hashlib
from typing import List
from sqlalchemy import text
from redis import asyncio as aioredis
from app.core.config import settings
from app.core.database import engine
from .memory_service import _embed  # Reuse the embedding helper

# Global Redis Pool
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def _get_cache_key(user_id: int, query: str) -> str:
    """Generate a stable cache key for a specific query."""
    query_hash = hashlib.md5(query.strip().lower().encode()).hexdigest()
    return f"rag_cache:{user_id}:{query_hash}"

async def store_user_knowledge(
    user_id: int,
    category: str, # e.g., "brand_voice", "audience", "guidelines"
    content: str,
) -> None:
    """Store general user knowledge for RAG and invalidate cache."""
    print(f"Creating embedding for content (len: {len(content)})")
    vector = await _embed(content)
    print(f"Embedding created (dim: {len(vector)})")
    
    async with engine.begin() as conn:
        print(f"Inserting knowledge into DB for user {user_id}")
        await conn.execute(
            text("""
                INSERT INTO ai_agent_memory (id, user_id, agent_kind, content, embedding)
                VALUES (:id, :user_id, :agent_kind, :content, CAST(:embedding AS vector))
            """),
            {
                "id":         str(uuid.uuid4()),
                "user_id":    user_id,
                "agent_kind": f"knowledge_{category}",
                "content":    content,
                "embedding":  str(vector),
            },
        )
        print("Knowledge inserted successfully")
    
    # Invalidate all RAG cache for this user
    try:
        print(f"Invalidating Redis cache for user {user_id}")
        async for key in redis_client.scan_iter(f"rag_cache:{user_id}:*"):
            await redis_client.delete(key)
        print("Cache invalidation complete")
    except Exception as re:
        print(f"Redis Cache Invalidation Warning (non-fatal): {re}")

async def search_user_knowledge(
    user_id: int,
    query: str,
    limit: int = 5,
) -> List[str]:
    """Retrieve relevant knowledge context for the user with Redis caching."""
    cache_key = await _get_cache_key(user_id, query)
    
    # 1. Try Cache First
    try:
        cached_val = await redis_client.get(cache_key)
        if cached_val:
            return json.loads(cached_val)
    except Exception as e:
        print(f"Redis Cache Error: {e}")

    # 2. Database Fallback (Vector Search)
    vector = await _embed(query)
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT content
                FROM   ai_agent_memory
                WHERE  user_id = :user_id
                  AND  agent_kind LIKE 'knowledge_%%'
                ORDER  BY embedding <=> CAST(:embedding AS vector)
                LIMIT  :limit
            """),
            {
                "user_id":    user_id,
                "embedding":  str(vector),
                "limit":      limit,
            },
        )
        hits = [row[0] for row in result.fetchall()]

    # 3. Cache the result for 1 hour
    try:
        if hits:
            await redis_client.set(cache_key, json.dumps(hits), ex=3600)
    except Exception as e:
        print(f"Redis Set Error: {e}")

    return hits

async def get_all_user_knowledge(user_id: int) -> List[dict]:
    """Retrieve all stored knowledge chunks for a user."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT id, content, agent_kind, created_at
                FROM   ai_agent_memory
                WHERE  user_id = :user_id
                  AND  agent_kind LIKE 'knowledge_%%'
                ORDER  BY created_at DESC
            """),
            {"user_id": user_id}
        )
        return [
            {
                "id": str(row[0]),
                "content": row[1],
                "category": row[2].replace("knowledge_", ""),
                "created_at": row[3].isoformat() if row[3] else None
            }
            for row in result.fetchall()
        ]
