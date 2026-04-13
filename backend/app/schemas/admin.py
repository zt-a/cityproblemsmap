# app/schemas/admin.py
from pydantic import BaseModel
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserAdminView(BaseModel):
    """Расширенный профиль пользователя для админа."""
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


class UserList(BaseModel):
    """Список пользователей с пагинацией."""
    items:  list[UserAdminView]
    total:  int
    offset: int
    limit:  int


class ChangeRoleRequest(BaseModel):
    """Смена роли пользователя."""
    role: UserRole


class SuspendRequest(BaseModel):
    """Блокировка пользователя."""
    reason: str


class SystemStats(BaseModel):
    """Общая статистика системы — только для admin."""
    total_users:       int
    active_users:      int
    suspended_users:   int
    total_problems:    int
    open_problems:     int
    solved_problems:   int
    rejected_problems: int
    total_votes:       int
    total_comments:    int
    total_media:       int
    cities_covered:    int   # уникальных городов с проблемами


class RejectProblemRequest(BaseModel):
    """Отклонение проблемы модератором."""
    reason: str