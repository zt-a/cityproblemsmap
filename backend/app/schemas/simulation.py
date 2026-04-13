# app/schemas/simulation.py
from pydantic import BaseModel, field_validator
from datetime import datetime
from app.models.simulation import SimEventType, SimEventStatus


class SimulationEventCreate(BaseModel):
    """Создание симуляционного события — только official/admin."""
    zone_entity_id: int
    event_type:     SimEventType
    title:          str
    description:    str | None = None

    # Временные рамки
    planned_start:  datetime | None = None
    planned_end:    datetime | None = None

    # Влияние на индексы зоны
    # Положительное = ухудшение, отрицательное = улучшение
    traffic_impact:   float = 0.0   # -1.0 до +1.0
    pollution_impact: float = 0.0
    risk_delta:       float = 0.0

    simulation_params: dict | None = None

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Минимум 5 символов")
        return v

    @field_validator("traffic_impact", "pollution_impact", "risk_delta")
    @classmethod
    def impact_range(cls, v: float) -> float:
        if not (-1.0 <= v <= 1.0):
            raise ValueError("Значение должно быть от -1.0 до +1.0")
        return v


class SimulationEventStatusUpdate(BaseModel):
    """Смена статуса события."""
    status:       SimEventStatus
    actual_start: datetime | None = None
    actual_end:   datetime | None = None


class SimulationEventPublic(BaseModel):
    """Публичные данные события."""
    entity_id:            int
    version:              int
    zone_entity_id:       int
    created_by_entity_id: int
    event_type:           SimEventType
    status:               SimEventStatus
    title:                str
    description:          str | None
    planned_start:        datetime | None
    planned_end:          datetime | None
    actual_start:         datetime | None
    actual_end:           datetime | None
    traffic_impact:       float
    pollution_impact:     float
    risk_delta:           float
    simulation_params:    dict | None
    is_current:           bool
    created_at:           datetime

    model_config = {"from_attributes": True}


class SimulationImpactPreview(BaseModel):
    """
    Предпросмотр влияния события на зону.
    Показывается перед созданием — "что изменится если запустить это событие".
    """
    zone_entity_id:          int
    zone_name:               str
    current_pollution_index: float
    current_traffic_index:   float
    current_risk_score:      float
    projected_pollution:     float   # после события
    projected_traffic:       float
    projected_risk:          float
    delta_summary:           str     # "Трафик вырастет на 20%, загрязнение не изменится"