# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, field_validator


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Минимум 8 символов")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Минимум 8 символов")
        return v


class LogoutRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    """Простой ответ с сообщением."""
    message: str