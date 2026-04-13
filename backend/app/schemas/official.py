# app/schemas/official.py
from pydantic import BaseModel
from datetime import datetime
from app.models.problem import ProblemType, ProblemStatus


class AssignedProblem(BaseModel):
    """Проблема назначенная на официала."""
    entity_id:        int
    title:            str
    description:      str | None
    city:             str
    district:         str | None
    address:          str | None
    problem_type:     ProblemType
    status:           ProblemStatus
    priority_score:   float
    created_at:       datetime
    latitude:         float | None
    longitude:        float | None

    model_config = {"from_attributes": True}


class AssignedProblemList(BaseModel):
    """Список назначенных проблем."""
    items:  list[AssignedProblem]
    total:  int
    offset: int
    limit:  int


class TakeProblemRequest(BaseModel):
    """Взять проблему в работу."""
    note: str | None = None


class ResolveProblemRequest(BaseModel):
    """Отметить проблему решённой с отчётом."""
    resolution_note: str
    actual_work_done: str | None = None  # что конкретно сделано


class OfficialCommentRequest(BaseModel):
    """Официальный ответ от городских служб."""
    content: str
    estimated_resolution_date: datetime | None = None


class OfficialZone(BaseModel):
    """Зона закреплённая за официалом."""
    entity_id:       int
    name:            str
    zone_type:       str
    city:            str
    total_problems:  int
    open_problems:   int
    solved_problems: int

    model_config = {"from_attributes": True}


class OfficialStats(BaseModel):
    """Статистика работы официала."""
    problems_assigned:    int  # назначено проблем
    problems_in_progress: int  # в работе
    problems_resolved:    int  # решено
    avg_resolution_days:  float | None  # среднее время решения
    zones_managed:        int  # зон под управлением
    official_responses:   int  # официальных ответов
