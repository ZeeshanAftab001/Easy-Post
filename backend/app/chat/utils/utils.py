from uuid import uuid4
from sqlalchemy import select
from ...chat.models import ChatSession
from sqlalchemy.ext.asyncio import AsyncSession

async def get_or_create_chat_session(
    db: AsyncSession,
    user_id: int,
    tenant_id: int
) -> ChatSession:

    stmt = select(ChatSession).where(ChatSession.user_id == user_id)
    result = await db.execute(stmt)
    chat = result.scalars().first()

    if chat:
        return chat

    chat = ChatSession(
        id=str(uuid4()),
        user_id=user_id,
        tenant_id=tenant_id
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat
