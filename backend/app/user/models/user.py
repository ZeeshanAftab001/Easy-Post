# app/user/models/user_model.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    whatsapp_number = Column(String, unique=True, nullable=False)
    niche = Column(String, nullable=False)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Change from: "app.chat.models.whatsapp.ChatSession"
    # To: Just "ChatSession"
    social_accounts = relationship(
        "SocialAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    chats = relationship(
        "ChatSession",  # ← JUST THE CLASS NAME
        back_populates="user",
        lazy="dynamic"  # Add this to prevent immediate loading issues
    )