# app/schemas/moderation.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class BanUserRequest(BaseModel):
    reason: str = Field(..., description="Причина блокировки")
    duration_days: Optional[int] = Field(None, description="Длительность в днях (None = постоянно)")


class UnbanUserRequest(BaseModel):
    reason: str = Field(..., description="Причина разблокировки")


class BanInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_banned: bool
    ban_reason: Optional[str]
    ban_until: Optional[datetime]
    banned_by_entity_id: Optional[int]
    banned_at: Optional[datetime]


class BannedUsersList(BaseModel):
    items: list[dict]
    total: int
    offset: int
    limit: int
