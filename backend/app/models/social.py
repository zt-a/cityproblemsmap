# app/models/social.py
from sqlalchemy import Column, Integer, String, Text, JSON
from app.models.mixins import VersionMixin
from app.database import Base


class UserProfile(VersionMixin, Base):
    """Расширенный профиль пользователя"""
    __tablename__ = "user_profiles"

    user_entity_id = Column(Integer, nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    social_links = Column(JSON, nullable=True)  # {"twitter": "...", "facebook": "..."}

    def __repr__(self):
        return f"<UserProfile(user={self.user_entity_id})>"


class Follow(VersionMixin, Base):
    """Подписки пользователей друг на друга"""
    __tablename__ = "follows"

    follower_entity_id = Column(Integer, nullable=False, index=True)
    following_entity_id = Column(Integer, nullable=False, index=True)

    def __repr__(self):
        return f"<Follow(follower={self.follower_entity_id}, following={self.following_entity_id})>"
