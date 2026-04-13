# app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole, UserStatus
from datetime import datetime


class UserRegister(BaseModel):
    """Данные для регистрации."""
    username: str
    email:    EmailStr
    password: str
    country:  str | None = None
    city:     str | None = None
    district: str | None = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Минимум 3 символа")
        if len(v) > 64:
            raise ValueError("Максимум 64 символа")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Минимум 8 символов")
        return v


class UserLogin(BaseModel):
    """Данные для логина."""
    email:    EmailStr
    password: str


class UserPublic(BaseModel):
    """Публичные данные пользователя — возвращаем в ответах."""
    entity_id:   int
    version:     int
    username:    str
    email:       str
    role:        UserRole
    status:      UserStatus
    country:     str | None
    city:        str | None
    district:    str | None
    reputation:  float
    is_verified: bool
    created_at:  datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Ответ после успешного логина/регистрации."""
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          UserPublic


class RefreshRequest(BaseModel):
    """Тело запроса для обновления токена."""
    refresh_token: str



class UpdateProfileRequest(BaseModel):
    """Смена username."""
    username: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Минимум 3 символа")
        if len(v) > 64:
            raise ValueError("Максимум 64 символа")
        return v


class UpdateEmailRequest(BaseModel):
    """Смена email — требует подтверждение паролем."""
    new_email:    EmailStr
    password:     str


class ReputationLogPublic(BaseModel):
    """Одна запись истории репутации."""
    id:                         int
    delta:                      float
    reason:                     str
    note:                       str | None
    related_problem_entity_id:  int | None
    snapshot_reputation:        float
    created_at:                 datetime

    model_config = {"from_attributes": True}


class ReputationHistory(BaseModel):
    """История репутации с текущим значением."""
    current_reputation: float
    logs:               list[ReputationLogPublic]