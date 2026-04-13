# app/models/subscription.py
from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.models.mixins import VersionMixin
from app.database import Base


class Subscription(VersionMixin, Base):
    __tablename__ = "subscriptions"

    user_entity_id = Column(Integer, nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # problem/zone/user
    target_entity_id = Column(Integer, nullable=False)
    notification_types = Column(JSON, nullable=False)  # ["email", "push"]

    def __repr__(self):
        return (
            f"<Subscription(entity_id={self.entity_id}, "
            f"user={self.user_entity_id}, "
            f"target={self.target_type}:{self.target_entity_id})>"
        )
