from pydantic import BaseModel
from typing import Optional, List

class PostState(BaseModel):
    platform: Optional[str] = None
    topic: Optional[str] = None
    tone: Optional[str] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    hashtags: List[str] = []
    approval_status: str = "pending"