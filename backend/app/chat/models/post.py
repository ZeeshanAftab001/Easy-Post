# app/chat/models/post.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    platform = Column(String, nullable=False)  # "facebook", "instagram", "all"
    status = Column(String, default="published")  # "draft", "scheduled", "published", "failed"
    schedule_time = Column(DateTime, nullable=True)
    platform_post_id = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True) # Store post-specific metadata or analytics snippets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="posts")

# Update User model to include posts relationship
# In app/user/models/user.py:
# posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
