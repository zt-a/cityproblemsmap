# app/schemas/notification.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.notification import NotificationType
from pydantic import ConfigDict

class NotificationBase(BaseModel):
    notification_type: NotificationType
    title: str = Field(..., max_length=255)
    message: str
    problem_id: Optional[int] = None
    comment_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    user_id: int
    actor_id: Optional[int] = None


class NotificationPublic(NotificationBase):
    model_config = ConfigDict(from_attributes=True)
    
    entity_id: int
    user_id: int
    actor_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime




class NotificationList(BaseModel):
    notifications: list[NotificationPublic]
    total: int
    unread_count: int


class MarkAsReadRequest(BaseModel):
    notification_ids: list[int] = Field(..., min_length=1)


class NotificationStats(BaseModel):
    total: int
    unread: int
    by_type: dict[str, int]
