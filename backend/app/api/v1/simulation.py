# app/api/v1/simulation.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.simulation import SimulationEvent, SimEventStatus
from app.models.zone import Zone
from app.models.user import User, UserRole
from app.schemas.simulation import (
    SimulationEventCreate,
    SimulationEventStatusUpdate,
    SimulationEventPublic,
    SimulationImpactPreview,
)
from app.services.versioning import create_new_version
from app.services.simulation import (
    preview_event_impact,
    apply_event_to_zone,
    revert_event_from_zone,
)
from app.api.deps import require_role

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post(
    "/preview",
    response_model=SimulationImpactPreview,
)
def preview_impact(
    zone_entity_id:   int,
    traffic_impact:   float = 0.0,
    pollution_impact: float = 0.0,
    risk_delta:       float = 0.0,
    db:               Session = Depends(get_db),
    current_user:     User    = Depends(
        require_role(UserRole.admin, UserRole.official)
    ),
):
    """
    Предпросмотр влияния события на зону.
    Вызывается перед созданием — показывает что изменится.

    Пример: дорожные работы на главной улице
    → трафик +30%, загрязнение +10%, риск +5%
    """
    return preview_event_impact(
        db               = db,
        zone_entity_id   = zone_entity_id,
        traffic_impact   = traffic_impact,
        pollution_impact = pollution_impact,
        risk_delta       = risk_delta,
    )


@router.post("/", response_model=SimulationEventPublic, status_code=201)
def create_event(
    data:         SimulationEventCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(
        require_role(UserRole.admin, UserRole.official)
    ),
):
    """
    Создать симуляционное событие.
    Только admin или official.

    Событие создаётся со статусом planned —
    индексы зоны не меняются до перевода в active.
    """

    # Проверить что зона существует
    zone = (
        db.query(Zone)
        .filter_by(entity_id=data.zone_entity_id, is_current=True)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Зона не найдена")

    entity_id = SimulationEvent.next_entity_id(db)

    event = SimulationEvent(
        entity_id            = entity_id,
        version              = 1,
        is_current           = True,
        zone_entity_id       = data.zone_entity_id,
        created_by_entity_id = current_user.entity_id,
        event_type           = data.event_type,
        status               = SimEventStatus.planned,
        title                = data.title,
        description          = data.description,
        planned_start        = data.planned_start,
        planned_end          = data.planned_end,
        traffic_impact       = data.traffic_impact,
        pollution_impact     = data.pollution_impact,
        risk_delta           = data.risk_delta,
        simulation_params    = data.simulation_params,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=list[SimulationEventPublic])
def list_events(
    zone_entity_id: int | None          = Query(None),
    status:         SimEventStatus | None = Query(None),
    db:             Session              = Depends(get_db),
):
    """
    Список событий с фильтрацией.
    Доступен публично — пользователи видят что планируется в городе.
    """
    query = db.query(SimulationEvent).filter_by(is_current=True)

    if zone_entity_id:
        query = query.filter(
            SimulationEvent.zone_entity_id == zone_entity_id
        )
    if status:
        query = query.filter(SimulationEvent.status == status)

    return (
        query
        .order_by(SimulationEvent.planned_start.asc())
        .all()
    )


@router.get("/{entity_id}", response_model=SimulationEventPublic)
def get_event(entity_id: int, db: Session = Depends(get_db)):
    """Получить событие по entity_id."""
    event = (
        db.query(SimulationEvent)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.patch("/{entity_id}/status", response_model=SimulationEventPublic)
def update_event_status(
    entity_id:    int,
    data:         SimulationEventStatusUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(
        require_role(UserRole.admin, UserRole.official)
    ),
):
    """
    Сменить статус события.

    Переходы статусов и их эффекты:
    planned → active    : применяет дельты к индексам зоны
    active  → completed : откатывает дельты (работы завершены)
    active  → cancelled : откатывает дельты (работы отменены)
    planned → cancelled : без изменений индексов (ещё не применялись)

    Каждый переход = новая версия события + новая версия зоны.
    """
    event = (
        db.query(SimulationEvent)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    # Валидация переходов статусов
    allowed_transitions = {
        SimEventStatus.planned:   {SimEventStatus.active, SimEventStatus.cancelled},
        SimEventStatus.active:    {SimEventStatus.completed, SimEventStatus.cancelled},
        SimEventStatus.completed: set(),   # финальный статус
        SimEventStatus.cancelled: set(),   # финальный статус
    }

    if data.status not in allowed_transitions[event.status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Нельзя перейти из {event.status.value} в {data.status.value}. "
                f"Допустимо: {[s.value for s in allowed_transitions[event.status]]}"
            ),
        )

    # Поля для новой версии события
    fields: dict = {"status": data.status}

    if data.status == SimEventStatus.active:
        fields["actual_start"] = data.actual_start or datetime.now(timezone.utc)

    if data.status in (SimEventStatus.completed, SimEventStatus.cancelled):
        fields["actual_end"] = data.actual_end or datetime.now(timezone.utc)

    # Создаём новую версию события
    updated_event = create_new_version(
        db            = db,
        model_class   = SimulationEvent,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"status_update_to_{data.status.value}",
        **fields,
    )

    # Применяем или откатываем влияние на зону
    if data.status == SimEventStatus.active:
        # planned → active: применить дельты к индексам зоны
        apply_event_to_zone(db=db, event=updated_event)

    elif data.status in (SimEventStatus.completed, SimEventStatus.cancelled):
        # active → completed/cancelled: откатить дельты
        # Откатываем только если событие было активным
        if event.status == SimEventStatus.active:
            revert_event_from_zone(db=db, event=event)

    return updated_event


@router.get("/{entity_id}/history", response_model=list[SimulationEventPublic])
def get_event_history(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(
        require_role(UserRole.admin, UserRole.official)
    ),
):
    """
    История версий события.
    Показывает все смены статуса с временными метками.
    """
    versions = (
        db.query(SimulationEvent)
        .filter_by(entity_id=entity_id)
        .order_by(SimulationEvent.version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return versions