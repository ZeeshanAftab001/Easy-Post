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
    whatsapp_lid = Column(String, unique=True, nullable=True)  # WAHA LID (auto-populated on first message)
    verification_status = Column(String, default="pending")  # pending / verified
    verification_code = Column(String, nullable=True)
    code_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    niche = Column(String, nullable=False)
    display_name = Column(String, nullable=True) # From WhatsApp notifyName
    ai_tone = Column(String, nullable=True, default="Analytical")
    broadcast_timing = Column(String, nullable=True, default="System Optimization Active")
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    social_accounts = relationship(
        "SocialAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan"
    )

# Avoid circular imports but allow SQLAlchemy to find models
from ...chat.models.post import Post
from ...oauth.models.social import SocialAccount
