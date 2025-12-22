from fastapi import APIRouter, Request, Query, Depends
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse

from ..services.agent_service import agent
from ..services.whatsapp_service import send_text, handle_text, handle_media
from ...core.database import get_db
from ...core.config import settings
from ...user.services.user_service import get_user_by_number
from sqlalchemy.ext.asyncio import AsyncSession
from ..utils.utils import save_message,load_chat_history,get_or_create_chat_session



whatsapp_router = APIRouter()


@whatsapp_router.get("/webhook")
async def verify(
        hub_mode: str = Query(None, alias="hub.mode"),
        hub_verify_token: str = Query(None, alias="hub.verify_token"),
        hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    return PlainTextResponse("Verification failed", status_code=403)


@whatsapp_router.post("/webhook")
async def receive_message(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    data = await request.json()

    entry = data.get("entry", [])
    if not entry:
        return {"status": "no entry"}

    changes = entry[0].get("changes", [])
    value = changes[0].get("value", {})

    if "messages" not in value:
        return {"status": "ignored"}

    message = value["messages"][0]
    sender = message["from"]
    msg_type = message.get("type")

    # 1️⃣ Get user
    user = await get_user_by_number(db, sender)
    if not user:
        return await send_text(sender, "You are not a registered user.")

    # 2️⃣ Get or create chat session
    chat = await get_or_create_chat_session(
        db=db,
        user_id=user.id,
    )

    # 3️⃣ Handle text messages
    if msg_type == "text":
        user_text = message["text"]["body"]

        # Save USER message
        await save_message(db, chat.id, "user", user_text)

        # Load history for agent
        messages = await load_chat_history(db, chat.id)

        # 4️⃣ Call LangGraph agent
        result = await agent.ainvoke(
            {"messages": messages},
            config={
                "configurable": {
                    "thread_id": chat.id
                }
            }
        )

        ai_text = result["messages"][-1].content

        # Save AI message
        await save_message(db, chat.id, "assistant", ai_text)

        # Send back to WhatsApp
        await send_text(sender, ai_text)

    return {"status": "ok"}
