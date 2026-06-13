# app/chat/routes/knowledge_router.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ...auth.services.auth_services import get_current_user
from ...user.models.user import User
from ..services.knowledge_service import store_user_knowledge, get_all_user_knowledge
from pydantic import BaseModel


knowledge_router = APIRouter(tags=["ai-knowledge"])

class KnowledgeInput(BaseModel):
    category: str
    content: str

@knowledge_router.get("/")
async def get_knowledge(
    current_user: User = Depends(get_current_user)
):
    """Retrieve all existing knowledge for the user."""
    try:
        data = await get_all_user_knowledge(user_id=current_user.id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@knowledge_router.post("/")
async def add_user_knowledge(
    req: KnowledgeInput,
    current_user: User = Depends(get_current_user)
):
    """Add context to the user's vector knowledge base."""
    try:
        await store_user_knowledge(
            user_id=current_user.id,
            category=req.category,
            content=req.content
        )
        return {"message": "Knowledge indexed successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
