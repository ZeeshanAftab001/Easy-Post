from uuid import uuid4
from ..models.whatsapp import ChatSession,ChatMemory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

async def get_or_create_chat_session(
    db: AsyncSession,
    user_id: int,
) -> ChatSession:

    stmt = select(ChatSession).where(ChatSession.user_id == user_id)
    result = await db.execute(stmt)
    chat = result.scalars().first()

    if chat:
        return chat

    chat = ChatSession(
        id=str(uuid4()),
        user_id=user_id,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def save_message(
    db: AsyncSession,
    chat_id: str,
    role: str,
    content: str
):
    memory = ChatMemory(
        chat_id=chat_id,
        role=role,
        content=content
    )
    db.add(memory)
    await db.commit()

async def load_chat_history(db: AsyncSession, chat_id: str):
    stmt = (
        select(ChatMemory)
        .where(ChatMemory.chat_id == chat_id)
        .order_by(ChatMemory.created_at)
    )
    result = await db.execute(stmt)
    memories = result.scalars().all()

    messages = []
    for m in memories:
        if m.role == "user":
            messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            messages.append(AIMessage(content=m.content))
        elif m.role == "system":
            messages.append(SystemMessage(content=m.content))

    return messages
