# app/chat/routes/whatsapp_router.py
from fastapi import APIRouter, Request, Query, Depends
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse
from langchain_core.messages import HumanMessage
# CHANGE: Import get_agent instead of agent_instance
# from ..services.agent_service import get_agent_for_request
from ..services.whatsapp_service import send_text, handle_text, handle_media
from ...core.database import get_db
from ...core.config import settings
from ...user.services.user_service import get_user_by_number
from sqlalchemy.ext.asyncio import AsyncSession

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
    
    print("-"*10, sender)
    print("-"*10, message)

    # 1️⃣ Get user
    user = await get_user_by_number(db, sender)
    if not user:
        return await send_text(sender, "You are not a registered user.")

    
    # 3️⃣ Handle text messages
    if msg_type == "text":
        user_text = message["text"]["body"]

        # 4️⃣ Call LangGraph agent
        # CHANGE: Use get_agent() instead of agent_instance
        agent = request.app.state.graph
        result = await agent.ainvoke(
            #{"messages": [HumanMessage(content=user_text)]},
            {"messages": user_text},
            config={"configurable": {"thread_id": user.whatsapp_number}}
        )
        # ai_text = result["messages"][-1].content
        ai_text = result["messages"]

        # Send back to WhatsApp
        await send_text(sender, ai_text)

    return {"status": "ok"}