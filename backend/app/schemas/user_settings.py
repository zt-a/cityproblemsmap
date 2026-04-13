# app/schemas/user_settings.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserNotificationSettingsBase(BaseModel):
    email_enabled: bool = True
    email_on_comment: bool = True
    email_on_status_change: bool = True
    email_on_official_response: bool = True
    email_on_problem_solved: bool = True
    email_on_mention: bool = True

    push_enabled: bool = False
    push_on_comment: bool = True
    push_on_status_change: bool = True

    digest_enabled: bool = True
    digest_frequency: str = Field(default="weekly", pattern="^(daily|weekly|monthly)$")
    digest_day: Optional[int] = Field(default=None, ge=0, le=31)

    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[int] = Field(default=None, ge=0, le=23)
    quiet_hours_end: Optional[int] = Field(default=None, ge=0, le=23)


class UserNotificationSettingsCreate(UserNotificationSettingsBase):
    pass


class UserNotificationSettingsUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    email_on_comment: Optional[bool] = None
    email_on_status_change: Optional[bool] = None
    email_on_official_response: Optional[bool] = None
    email_on_problem_solved: Optional[bool] = None
    email_on_mention: Optional[bool] = None

    push_enabled: Optional[bool] = None
    push_on_comment: Optional[bool] = None
    push_on_status_change: Optional[bool] = None

    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = Field(default=None, pattern="^(daily|weekly|monthly)$")
    digest_day: Optional[int] = Field(default=None, ge=0, le=31)

    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = Field(default=None, ge=0, le=23)
    quiet_hours_end: Optional[int] = Field(default=None, ge=0, le=23)


class UserNotificationSettingsPublic(UserNotificationSettingsBase):
    model_config = ConfigDict(from_attributes=True)
    entity_id: int
    user_entity_id: int
    version: int