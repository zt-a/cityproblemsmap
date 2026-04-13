# app/schemas/subscription.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime



class SubscriptionCreate(BaseModel):
    notification_types: list[str] = Field(
        default=["email"],
        description="Типы уведомлений: email, push"
    )


class SubscriptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    entity_id: int
    version: int
    is_current: bool
    created_at: datetime
    user_entity_id: int
    target_type: str
    target_entity_id: int
    notification_types: list[str]


class SubscriptionList(BaseModel):
    items: list[SubscriptionPublic]
    total: int
