# app/chat/routes/media_router.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ...auth.services.auth_services import get_current_user
from ...user.models.user import User
from ...core.s3_service import s3_service

media_router = APIRouter(tags=["media"])

@media_router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload media to S3 for use in social posts."""
    print(f"[UPLOAD] Received file: {file.filename}, content_type: {file.content_type}")
    if file.content_type not in s3_service.ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    
    try:
        content = await file.read()
        s3_url = await s3_service.upload_image(
            content, 
            mime_type=file.content_type, 
            folder=f"user_{current_user.id}/dashboard"
        )
        
        if not s3_url:
            raise HTTPException(status_code=500, detail="S3 upload failed")
            
        print(f"[UPLOAD] S3 URL: {s3_url}")
        return {"url": s3_url}
    except Exception as e:
        print(f"[UPLOAD] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
