# app/services/simulation.py
from sqlalchemy.orm import Session
from app.models.zone import Zone
from app.models.simulation import SimulationEvent
from app.schemas.simulation import SimulationImpactPreview
from app.services.versioning import create_new_version


def preview_event_impact(
    db:             Session,
    zone_entity_id: int,
    traffic_impact:   float,
    pollution_impact: float,
    risk_delta:       float,
) -> SimulationImpactPreview:
    """
    Считает как событие изменит индексы зоны.
    Вызывается до создания — пользователь видит превью.

    Логика: новый_индекс = clamp(текущий + delta, 0.0, 1.0)
    clamp — не даёт выйти за пределы 0.0–1.0.
    """
    zone = (
        db.query(Zone)
        .filter_by(entity_id=zone_entity_id, is_current=True)
        .first()
    )
    if not zone:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Зона не найдена")

    def clamp(val: float) -> float:
        return round(max(0.0, min(1.0, val)), 4)

    projected_pollution = clamp(zone.pollution_index + pollution_impact)
    projected_traffic   = clamp(zone.traffic_index   + traffic_impact)
    projected_risk      = clamp(zone.risk_score      + risk_delta)

    # Текстовое описание изменений
    parts = []
    if abs(traffic_impact) > 0.01:
        direction = "вырастет" if traffic_impact > 0 else "снизится"
        parts.append(f"Трафик {direction} на {abs(traffic_impact)*100:.0f}%")
    if abs(pollution_impact) > 0.01:
        direction = "вырастет" if pollution_impact > 0 else "снизится"
        parts.append(f"Загрязнение {direction} на {abs(pollution_impact)*100:.0f}%")
    if abs(risk_delta) > 0.01:
        direction = "вырастет" if risk_delta > 0 else "снизится"
        parts.append(f"Риск {direction} на {abs(risk_delta)*100:.0f}%")

    delta_summary = ". ".join(parts) if parts else "Индексы зоны не изменятся"

    return SimulationImpactPreview(
        zone_entity_id          = zone.entity_id,
        zone_name               = zone.name,
        current_pollution_index = zone.pollution_index,
        current_traffic_index   = zone.traffic_index,
        current_risk_score      = zone.risk_score,
        projected_pollution     = projected_pollution,
        projected_traffic       = projected_traffic,
        projected_risk          = projected_risk,
        delta_summary           = delta_summary,
    )


def apply_event_to_zone(
    db:    Session,
    event: SimulationEvent,
) -> Zone:
    """
    Применяет влияние активного события на индексы зоны.
    Вызывается когда событие переходит в статус active.
    Создаёт новую версию зоны с обновлёнными индексами.
    """
    zone = (
        db.query(Zone)
        .filter_by(entity_id=event.zone_entity_id, is_current=True)
        .first()
    )
    if not zone:
        return None

    def clamp(val: float) -> float:
        return round(max(0.0, min(1.0, val)), 4)

    updated_zone = create_new_version(
        db              = db,
        model_class     = Zone,
        entity_id       = zone.entity_id,
        changed_by_id   = event.created_by_entity_id,
        change_reason   = f"sim_event_{event.entity_id}_activated",
        pollution_index = clamp(zone.pollution_index + event.pollution_impact),
        traffic_index   = clamp(zone.traffic_index   + event.traffic_impact),
        risk_score      = clamp(zone.risk_score      + event.risk_delta),
    )
    return updated_zone


def revert_event_from_zone(
    db:    Session,
    event: SimulationEvent,
) -> Zone:
    """
    Откатывает влияние завершённого или отменённого события.
    Вызывается когда событие переходит в completed/cancelled.
    Вычитает те же дельты что были применены при активации.
    """
    zone = (
        db.query(Zone)
        .filter_by(entity_id=event.zone_entity_id, is_current=True)
        .first()
    )
    if not zone:
        return None

    def clamp(val: float) -> float:
        return round(max(0.0, min(1.0, val)), 4)

    # Откат = применяем обратные дельты
    updated_zone = create_new_version(
        db              = db,
        model_class     = Zone,
        entity_id       = zone.entity_id,
        changed_by_id   = event.created_by_entity_id,
        change_reason   = f"sim_event_{event.entity_id}_reverted",
        pollution_index = clamp(zone.pollution_index - event.pollution_impact),
        traffic_index   = clamp(zone.traffic_index   - event.traffic_impact),
        risk_score      = clamp(zone.risk_score      - event.risk_delta),
    )
    return updated_zone