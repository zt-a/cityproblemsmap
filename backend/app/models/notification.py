# app/models/notification.py
from sqlalchemy import Column, Integer, String, Boolean, Text, Enum as SQLEnum
from app.database import Base
from app.models.mixins import VersionMixin
import enum


class NotificationType(str, enum.Enum):
    """Типы уведомлений"""
    PROBLEM_STATUS_CHANGED = "problem_status_changed"
    PROBLEM_ASSIGNED = "problem_assigned"
    PROBLEM_COMMENTED = "problem_commented"
    COMMENT_REPLIED = "comment_replied"
    PROBLEM_UPVOTED = "problem_upvoted"
    PROBLEM_VERIFIED = "problem_verified"
    PROBLEM_REJECTED = "problem_rejected"
    COMMENT_HIDDEN = "comment_hidden"
    USER_MENTIONED = "user_mentioned"
    PROBLEM_SUBSCRIBED = "problem_subscribed"

    def __str__(self):
        return self.value


class Notification(VersionMixin, Base):
    """Модель уведомлений для пользователей с версионированием"""
    __tablename__ = "notifications"

    # Получатель уведомления
    user_entity_id = Column(Integer, nullable=False, index=True)

    # Тип уведомления
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)

    # Заголовок и текст уведомления
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Ссылка на связанные объекты
    problem_entity_id = Column(Integer, nullable=True, index=True)
    comment_entity_id = Column(Integer, nullable=True, index=True)

    # ID пользователя, который вызвал событие (опционально)
    actor_entity_id = Column(Integer, nullable=True)

    # Статус прочтения
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    def __repr__(self):
        return f"<Notification(entity_id={self.entity_id}, type={self.notification_type}, user={self.user_entity_id}, read={self.is_read})>"
