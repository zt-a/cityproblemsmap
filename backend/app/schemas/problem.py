# app/schemas/problem.py
from pydantic import BaseModel, field_validator
from app.models.problem import ProblemType, ProblemNature, ProblemStatus
from datetime import datetime 

class ProblemCreate(BaseModel):
    """Данные для создания новой проблемы."""
    title:        str
    description:  str | None = None
    country:      str = "Kyrgyzstan"
    city:         str
    district:     str | None = None
    address:      str | None = None
    latitude:     float       # координата на карте
    longitude:    float
    problem_type: ProblemType
    nature:       ProblemNature = ProblemNature.permanent
    tags:         list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Минимум 5 символов")
        return v

    @field_validator("latitude")
    @classmethod
    def lat_valid(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError("Широта должна быть от -90 до 90")
        return v

    @field_validator("longitude")
    @classmethod
    def lon_valid(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError("Долгота должна быть от -180 до 180")
        return v


class ProblemUpdate(BaseModel):
    """Обновление проблемы (только автор)."""
    title:        str | None = None
    description:  str | None = None
    address:      str | None = None
    latitude:     float | None = None
    longitude:    float | None = None
    problem_type: ProblemType | None = None
    tags:         list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 5:
                raise ValueError("Минимум 5 символов")
        return v

    @field_validator("latitude")
    @classmethod
    def lat_valid(cls, v: float | None) -> float | None:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("Широта должна быть от -90 до 90")
        return v

    @field_validator("longitude")
    @classmethod
    def lon_valid(cls, v: float | None) -> float | None:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("Долгота должна быть от -180 до 180")
        return v


class ProblemStatusUpdate(BaseModel):
    """Обновление статуса проблемы."""
    status:          ProblemStatus
    resolution_note: str | None = None


class ProblemPublic(BaseModel):
    """Публичные данные проблемы — возвращаем в ответах."""
    entity_id:            int
    version:              int
    author_entity_id:     int
    zone_entity_id:       int | None
    title:                str
    description:          str | None
    country:              str
    city:                 str
    district:             str | None
    address:              str | None
    latitude:             float | None  # достаём из PostGIS POINT
    longitude:            float | None
    problem_type:         ProblemType
    nature:               ProblemNature
    status:               ProblemStatus
    resolved_by_entity_id: int | None      # ← добавили
    resolved_at:          datetime | None       # ← добавили
    resolution_note:      str | None       # ← добавили
    truth_score:          float
    urgency_score:        float
    impact_score:         float
    inconvenience_score:  float
    priority_score:       float
    vote_count:           int
    comment_count:        int
    tags:                 list[str] | None
    change_reason:        str | None       # ← полезно для истории
    created_at:           datetime | None       # ← когда создана эта версия

    model_config = {"from_attributes": True}


class ProblemList(BaseModel):
    """Список проблем с пагинацией."""
    items:  list[ProblemPublic]
    total:  int
    offset: int
    limit:  int