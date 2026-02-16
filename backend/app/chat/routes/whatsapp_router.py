from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import PlainTextResponse
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession
import json
# from app.chat.services.whatsapp_service import send_text
# from ..services.whatsapp_service import send_text
from app.core.database import get_db
from app.core.config import settings
from app.user.services.user_service import get_user_by_number
from app.chat.services.agent_service import show_state
from app.chat.services.whatsapp_service import send_text,handle_text

whatsapp_router = APIRouter()

@whatsapp_router.get("/webhook")
async def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    return PlainTextResponse("Verification failed", status_code=403)


@whatsapp_router.post("/webhook")
async def receive_message(
    request: Request,
    db: AsyncSession = Depends(get_db),
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

    # print("📩 WhatsApp from:", sender)
    # print(message)

    # 1️⃣ Get user
    user = await get_user_by_number(db, sender)
    if not user:
        await send_text(sender, "You are not a registered user.")
        return {"status": "unauthorized"}

    # 2️⃣ Handle text
    if msg_type == "text":
        user_text = message["text"]["body"]

        agent = request.app.state.graph

        # 🔑 VERY IMPORTANT: stable thread_id
        thread_id = user.whatsapp_number

        # ✅ ONLY pass the NEW message
        result = await agent.ainvoke(
            {
                "messages": [HumanMessage(content=user_text)],
                "user_id": int(user.id),

            },
            config={"configurable": {"thread_id": thread_id}},
        )
        
        ai_text = result["messages"][-1].content
        
        # print("🤖 AI Response:", ai_text)
        # print("_" * 40)
        config={"configurable": {"thread_id": thread_id}}
        # print("📌 CURRENT HISTORY:")
        await show_state(agent, config=config)
        # print("_" * 40)
        # await send_text(sender, ai_text)
        await send_text(sender,ai_text )

    return {"status": "ok"}
