# app/chat/services/memory_service.py
#
# Per-agent vector memory using pgvector.
# Each agent_kind ("content", "strategy", "engagement") has isolated memory.
#
# Required DB setup:
#   CREATE EXTENSION IF NOT EXISTS vector;
#   CREATE TABLE ai_agent_memory (
#       id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#       user_id     INTEGER NOT NULL,
#       agent_kind  TEXT    NOT NULL,   -- "content" | "strategy" | "engagement"
#       content     TEXT    NOT NULL,
#       embedding   VECTOR(1536),
#       created_at  TIMESTAMP DEFAULT now()
#   );
#   CREATE INDEX ON ai_agent_memory USING ivfflat (embedding vector_cosine_ops);

from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import text
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.database import engine          # your existing async SQLAlchemy engine

_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def _embed(text_input: str) -> List[float]:
    resp = await _openai.embeddings.create(
        model="text-embedding-3-small",
        input=text_input,
    )
    return resp.data[0].embedding


async def store_agent_memory(
    user_id: int,
    agent_kind: str,
    content: str,
) -> None:
    """Persist a text chunk with its embedding, scoped to user + agent."""
    vector = await _embed(content)
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO ai_agent_memory (id, user_id, agent_kind, content, embedding)
                VALUES (:id, :user_id, :agent_kind, :content, CAST(:embedding AS vector))
            """),
            {
                "id":         str(uuid.uuid4()),
                "user_id":    user_id,
                "agent_kind": agent_kind,
                "content":    content,
                "embedding":  str(vector),
            },
        )


async def search_agent_memory(
    user_id: int,
    agent_kind: str,
    query: str,
    limit: int = 3,
) -> List[str]:
    """
    Retrieve the top-k most semantically similar memory chunks
    for a specific user + agent combination.
    """
    vector = await _embed(query)
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT content
                FROM   ai_agent_memory
                WHERE  user_id    = :user_id
                  AND  agent_kind = :agent_kind
                ORDER  BY embedding <=> CAST(:embedding AS vector)
                LIMIT  :limit
            """),
            {
                "user_id":    user_id,
                "agent_kind": agent_kind,
                "embedding":  str(vector),
                "limit":      limit,
            },
        )
        return [row[0] for row in result.fetchall()]
