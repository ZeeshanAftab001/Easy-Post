# app/chat/routes/whatsapp_router.py
from fastapi import APIRouter, Request, Depends
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.chat.services.whatsapp_formatter import md_to_wa
from app.core.database import get_db
from app.user.services.user_service import (
    get_user_by_number, 
    get_user_by_number_or_lid, 
    save_whatsapp_lid,
    verify_user
)
from app.chat.services.whatsapp_service import send_text
from app.core.config import settings
from app.platforms.whatsapp_downloader import download_whatsapp_media
from app.core.s3_service import s3_service

whatsapp_router = APIRouter()


async def _resolve_sender(sender_full: str, db: AsyncSession, payload: dict = {}):
    """
    Permanently resolve a WAHA sender to a User.

    WAHA can send messages using either:
      - Real phone number: "923332112684@c.us"
      - WhatsApp internal LID: "255799712591939@lid"

    According to WAHA docs, each user has BOTH a real @c.us ID and a hidden @lid.
    The webhook may include the real number in other payload fields.

    Resolution priority:
      1. Fast DB lookup by raw identifier (phone or cached LID)
      2. Scan other payload fields for a @c.us companion to the LID
      3. Call WAHA contacts API to resolve LID → real phone
      4. On success, store the LID on user for instant future lookups
    """
    sender_raw = sender_full.split("@")[0]
    sender_type = sender_full.split("@")[1] if "@" in sender_full else "c.us"

    # ── Step 1: Fast path — direct DB lookup ─────────────────────────────────
    user = await get_user_by_number_or_lid(db, sender_raw)
    if user:
        return user, sender_raw

    # ── Step 2: Not a LID — just not registered ───────────────────────────────
    if sender_type != "lid":
        return None, sender_raw

    print(f"🔍 Unknown LID '{sender_raw}' — scanning payload for @c.us partner...")

    # ── Step 3: Scan all payload fields for a real @c.us phone number ─────────
    # Per WAHA docs: each user has a regular @c.us ID alongside their @lid
    # It may appear in chatId, _data subfields, or other locations
    def extract_cus_numbers(obj, found=None):
        """Recursively find all @c.us IDs in the payload."""
        if found is None:
            found = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str) and "@c.us" in v:
                    found.add(v.split("@")[0])
                elif isinstance(v, str) and "@s.whatsapp.net" in v:
                    # docs say convert @s.whatsapp.net → @c.us
                    found.add(v.split("@")[0])
                else:
                    extract_cus_numbers(v, found)
        elif isinstance(obj, list):
            for item in obj:
                extract_cus_numbers(item, found)
        return found

    cus_numbers = extract_cus_numbers(payload)
    print(f"   Found @c.us candidates in payload: {cus_numbers}")

    for candidate in cus_numbers:
        user = await get_user_by_number(db, candidate)
        if user:
            print(f"✅ Resolved LID via payload scan: {sender_raw} → {candidate}")
            await save_whatsapp_lid(db, user, sender_raw)
            return user, candidate

    # ── Step 4: Call WAHA contacts API ────────────────────────────────────────
    print(f"   No match in payload — querying WAHA contacts API...")
    waha_headers = {}
    if settings.WAHA_API_KEY:
        waha_headers["X-Api-Key"] = settings.WAHA_API_KEY

    try:
        async with httpx.AsyncClient(headers=waha_headers, timeout=10) as client:
            resp = await client.get(
                f"{settings.WAHA_URL}/api/contacts",
                params={"contactId": sender_full, "session": settings.WAHA_SESSION},
            )
            if resp.status_code == 200:
                contact = resp.json()
                print(f"   WAHA contacts response: {contact}")
                real_id = contact.get("id") or contact.get("number") or ""
                candidate = real_id.split("@")[0]
                if candidate and candidate.isdigit():
                    user = await get_user_by_number(db, candidate)
                    if user:
                        print(f"✅ Resolved LID via WAHA API: {sender_raw} → {candidate}")
                        await save_whatsapp_lid(db, user, sender_raw)
                        return user, candidate
            else:
                print(f"⚠️ WAHA contacts API {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"⚠️ WAHA contacts API error: {e}")

    print(f"❌ Could not resolve LID '{sender_raw}'. Register this number in the DB.")
    return None, sender_raw



@whatsapp_router.post("/webhook")
async def receive_waha_message(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles incoming webhooks from WAHA (WhatsApp HTTP API).
    Self-healing: automatically resolves & caches WhatsApp LIDs on first contact.
    """
    try:
        data = await request.json()

        # WAHA Webhook Payload: { "event": "...", "session": "...", "payload": { ... } }
        event = data.get("event")
        if event != "message":
            return {"status": "ignored", "event": event}

        payload = data.get("payload", {})

        # Ignore messages sent by the bot itself
        if payload.get("fromMe"):
            return {"status": "ignored", "reason": "from_me"}

        sender_full = payload.get("from", "")
        body        = payload.get("body", "")
        has_media   = payload.get("hasMedia", False)
        media       = payload.get("media") if has_media else None

        print(f"📨 Incoming from: {sender_full} | Body: {body[:60]}")
        print(f"   Full payload keys: {list(payload.keys())}")

        user, sender = await _resolve_sender(sender_full, db, payload)
        if not user:
            print(f"❌ Unauthorized Operator: {sender_full}")
            return {"status": "unauthorized"}

        # ── Step 2: Handle Phone Verification Flow ────────────────────────────
        if user.verification_status == "pending":
            if body.strip().upper() == "DONE":
                # Capture the precise LID (sender_full) if it's a @lid address
                # sender_raw would be just the ID part. 
                # verify_user stores sender_raw as the LID.
                sender_raw = sender_full.split("@")[0]
                await verify_user(db, user, sender_raw)
                await send_text(sender_full, "✅ *Verification Successful!*\n\nYour WhatsApp account is now linked to Easy-Post. You can now start sending messages or media to the AI agent.")
                return {"status": "verified"}
            else:
                await send_text(sender_full, "⚠️ *Account Not Verified*\n\nPlease reply with *DONE* to verify your phone number and activate your account.")
                return {"status": "pending_verification"}

        agent     = request.app.state.graph
        thread_id = user.whatsapp_number
        config    = {"configurable": {"thread_id": thread_id}}

        # ── Handle Media (Images) ─────────────────────────────────────────────
        if has_media and media:
            media_id  = media.get("id")
            media_url = media.get("url")
            mimetype  = media.get("mimetype", "image/jpeg")

            # --- FIXED: Mirror to S3 before passing to agent ---
            # Facebook cannot reach localhost:3000, so we mirror to a public S3 bucket
            s3_url = None
            if mimetype.startswith("image/"):
                try:
                    print(f"🔄 Mirroring WhatsApp media to S3 (Source: {media_id or media_url})")
                    image_bytes, actual_mime = await download_whatsapp_media(media_id or media_url)
                    s3_url = await s3_service.upload_image(
                        image_bytes, 
                        actual_mime, 
                        folder=f"user_{user.id}/whatsapp_mirror"
                    )
                    print(f"✅ Mirrored to S3: {s3_url}")
                except Exception as e:
                    print(f"⚠️ Media mirroring failed: {e}")
                    # Fallback to local URL if S3 fails (though it might still fail at FB side)
                    s3_url = media_url
            
            print(f"📸 WhatsApp Media URL: {media_url}")
            if s3_url:
                print(f"   S3 Mirrored URL: {s3_url}")
            print(f"   Media ID: {media_id} | MIME: {mimetype}")

            if mimetype.startswith("image/"):
                agent_msg = (
                    f"USER REQUEST: {body}\n\n"
                    f"📸 WhatsApp Media URL: {media_url}\n"
                    f"📸 S3 Mirrored URL: {s3_url or media_url}\n"
                    f"📸 Platform Media ID: {media_id or media_url}\n"
                    f"📸 MIME Type: {mimetype}\n\n"
                    "Please help the user with this media asset."
                )
                try:
                    result = await agent.ainvoke(
                        {
                            "messages": [HumanMessage(content=agent_msg)], 
                            "user_id": user.id, 
                            "niche": user.niche,
                            "ai_tone": user.ai_tone,
                        },
                        config=config,
                    )
                    if "__interrupt__" in result:
                        interrupt_data = result["__interrupt__"][0]
                        # Handle both object and dict types for LangGraph versions
                        if hasattr(interrupt_data, "value"):
                            interrupt_val = interrupt_data.value
                        else:
                            interrupt_val = interrupt_data.get("value", {})
                        
                        interrupt_msg = interrupt_val.get("message", "Waiting for approval.")
                        await send_text(sender_full, interrupt_msg)
                        return {"status": "awaiting_approval"}

                    last_ai = next((m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None)
                    reply = md_to_wa(last_ai.content) if last_ai else "✅ Asset Pipeline Triggered."
                    await send_text(sender_full, reply)
                    return {"status": "ok"}
                except Exception as e:
                    print(f"❌ WAHA Media Agent Error: {e}")
                    await send_text(sender_full, "⚠️ System Failure: Could not process media asset.")
                    return {"status": "agent_error"}

        # ── Handle Text ───────────────────────────────────────────────────────
        if body:
            try:
                result = await agent.ainvoke(
                    {
                        "messages": [HumanMessage(content=body)], 
                        "user_id": user.id, 
                        "niche": user.niche,
                        "ai_tone": user.ai_tone,
                    },
                    config=config,
                )
                if "__interrupt__" in result:
                    interrupt_data = result["__interrupt__"][0]
                    if hasattr(interrupt_data, "value"):
                        interrupt_val = interrupt_data.value
                    else:
                        interrupt_val = interrupt_data.get("value", {})
                    
                    interrupt_msg = interrupt_val.get("message", "Waiting for approval.")
                    await send_text(sender_full, interrupt_msg)
                    return {"status": "awaiting_approval"}

                last_ai = next((m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None)
                reply = md_to_wa(last_ai.content) if last_ai else "Protocol Executed."
                await send_text(sender_full, reply)
                return {"status": "ok"}
            except Exception as e:
                print(f"❌ WAHA Text Agent Error: {e}")
                await send_text(sender_full, "⚠️ AI Agent encountered a processing error.")
                return {"status": "agent_error"}

        return {"status": "no_content"}
    except Exception as e:
        print(f"🚨 WAHA Webhook Critical Error: {e}")
        return {"status": "critical_failure"}