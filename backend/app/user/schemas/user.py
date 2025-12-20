from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    whatsapp_number: str
    niche: str
    password: str


class UserSchema(UserBase):
    id: int

    class Config:
        from_attributes = True