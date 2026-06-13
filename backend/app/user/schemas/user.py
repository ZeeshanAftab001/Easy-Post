from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    whatsapp_number: str
    niche: str
    ai_tone: Optional[str] = "Analytical"
    broadcast_timing: Optional[str] = "System Optimization Active"
    password: str

class UserSchema(UserBase):
    id: int
    whatsapp_number: Optional[str]
    niche: Optional[str]
    ai_tone: Optional[str]
    broadcast_timing: Optional[str]
    verification_status: Optional[str]
    whatsapp_lid: Optional[str]

    class Config:
        from_attributes = True