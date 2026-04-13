# app/models/activity.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.models.mixins import VersionMixin
from app.database import Base


class Activity(VersionMixin, Base):
    __tablename__ = "activities"

    user_entity_id = Column(Integer, nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # created/updated/commented/voted/etc
    target_type = Column(String(50), nullable=False)  # problem/comment/user
    target_entity_id = Column(Integer, nullable=False)
    extra_data = Column(JSON, nullable=True)  # Дополнительные данные о действии
    description = Column(Text, nullable=True)  # Человекочитаемое описание

    def __repr__(self):
        return (
            f"<Activity(entity_id={self.entity_id}, "
            f"user={self.user_entity_id}, "
            f"action={self.action_type})>"
        )
