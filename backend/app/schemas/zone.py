# app/schemas/zone.py
from pydantic import BaseModel, field_validator


class ZoneCreate(BaseModel):
    """Создание новой зоны — только admin/official."""
    name:             str
    zone_type:        str        # country / city / district / neighborhood
    parent_entity_id: int | None = None
    country:          str | None = None
    city:             str | None = None
    center_lat:       float | None = None
    center_lon:       float | None = None
    extra_data:       dict  | None = None

    @field_validator("zone_type")
    @classmethod
    def zone_type_valid(cls, v: str) -> str:
        allowed = {"country", "city", "district", "neighborhood"}
        if v not in allowed:
            raise ValueError(f"zone_type должен быть одним из: {allowed}")
        return v

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Минимум 2 символа")
        return v


class ZonePublic(BaseModel):
    """Публичные данные зоны."""
    entity_id:        int
    version:          int
    name:             str
    zone_type:        str
    parent_entity_id: int   | None
    country:          str   | None
    city:             str   | None
    center_lat:       float | None
    center_lon:       float | None
    total_problems:   int
    open_problems:    int
    solved_problems:  int
    pollution_index:  float
    traffic_index:    float
    risk_score:       float
    extra_data:       dict  | None

    model_config = {"from_attributes": True}


class ZoneStats(BaseModel):
    """
    Детальная статистика зоны.
    Используется для Digital Twin дашборда.
    """
    entity_id:          int
    name:               str
    zone_type:          str
    total_problems:     int
    open_problems:      int
    solved_problems:    int
    rejected_problems:  int    # признаны фейком
    in_progress:        int
    solve_rate:         float  # solved / total — 0.0–1.0
    pollution_index:    float
    traffic_index:      float
    risk_score:         float
    top_problem_types:  list[dict]  # [{"type": "pothole", "count": 12}, ...]