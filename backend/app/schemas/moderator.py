# app/schemas/moderator.py
from pydantic import BaseModel
from datetime import datetime


class FlaggedComment(BaseModel):
    """Комментарий с жалобой."""
    entity_id:         int
    problem_entity_id: int
    author_entity_id:  int
    content:           str
    is_flagged:        bool
    flag_reason:       str | None
    created_at:        datetime

    model_config = {"from_attributes": True}


class FlaggedCommentList(BaseModel):
    """Список комментариев с жалобами."""
    items:  list[FlaggedComment]
    total:  int
    offset: int
    limit:  int


class SuspiciousProblem(BaseModel):
    """Подозрительная проблема с низким truth_score."""
    entity_id:      int
    title:          str
    city:           str
    author_entity_id: int
    truth_score:    float
    vote_count:     int
    status:         str
    created_at:     datetime

    model_config = {"from_attributes": True}


class SuspiciousProblemList(BaseModel):
    """Список подозрительных проблем."""
    items:  list[SuspiciousProblem]
    total:  int
    offset: int
    limit:  int


class VerifyProblemRequest(BaseModel):
    """Подтверждение проблемы модератором."""
    note: str | None = None


class HideCommentRequest(BaseModel):
    """Скрытие комментария."""
    reason: str


class ModeratorStats(BaseModel):
    """Статистика работы модератора."""
    problems_verified:  int  # подтверждённых проблем
    problems_rejected:  int  # отклонённых проблем
    comments_hidden:    int  # скрытых комментариев
    users_suspended:    int  # заблокированных пользователей
    flagged_pending:    int  # жалоб на рассмотрении
    suspicious_pending: int  # подозрительных проблем
