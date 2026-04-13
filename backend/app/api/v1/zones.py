# app/api/v1/zones.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.zone import Zone
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.zone import ZoneCreate, ZonePublic, ZoneStats
from app.schemas.problem import ProblemList
from app.services.zones import recalculate_zone_stats, get_zone_detailed_stats
from app.api.deps import require_role
from app.services.cache import (
    get_cached_zone_stats,
    cache_zone_stats,
    CacheService,
)

router = APIRouter(prefix="/zones", tags=["zones"])


@router.post("/", response_model=ZonePublic, status_code=201)
def create_zone(
    data:         ZoneCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_role(UserRole.admin, UserRole.official)),
):
    """
    Создать зону — только admin или official.
    Зоны создаются вручную администраторами системы.
    """

    # Проверить что родительская зона существует если передана
    if data.parent_entity_id is not None:
        parent = (
            db.query(Zone)
            .filter_by(entity_id=data.parent_entity_id, is_current=True)
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Родительская зона не найдена",
            )

    entity_id = Zone.next_entity_id(db)

    zone = Zone(
        entity_id        = entity_id,
        version          = 1,
        is_current       = True,
        name             = data.name,
        zone_type        = data.zone_type,
        parent_entity_id = data.parent_entity_id,
        country          = data.country,
        city             = data.city,
        center_lat       = data.center_lat,
        center_lon       = data.center_lon,
        extra_data       = data.extra_data,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/", response_model=list[ZonePublic])
def list_zones(
    zone_type: str | None = Query(None, description="country / city / district / neighborhood"),
    city:      str | None = Query(None, description="Фильтр по городу"),
    db:        Session    = Depends(get_db),
):
    """
    Список всех зон.
    Используется для построения иерархии на карте.
    """
    # Кешируем список зон
    cache_key = f"zones:list:{zone_type or 'all'}:{city or 'all'}"
    cached = CacheService.get(cache_key)
    if cached:
        return [ZonePublic(**z) for z in cached]

    query = db.query(Zone).filter_by(is_current=True)

    if zone_type:
        query = query.filter(Zone.zone_type == zone_type)
    if city:
        query = query.filter(Zone.city == city)

    zones = query.order_by(Zone.name).all()

    # Кешируем на 15 минут (зоны меняются редко)
    CacheService.set(cache_key, [z.__dict__ for z in zones], ttl=900)

    return zones


@router.get("/{entity_id}", response_model=ZonePublic)
def get_zone(entity_id: int, db: Session = Depends(get_db)):
    """Получить зону по entity_id."""
    zone = (
        db.query(Zone)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Зона не найдена")
    return zone


@router.get("/{entity_id}/stats", response_model=ZoneStats)
def get_zone_stats(entity_id: int, db: Session = Depends(get_db)):
    """
    Детальная статистика зоны для Digital Twin дашборда.
    Включает распределение по типам проблем и индексы.
    """
    # Проверяем кеш
    cached = get_cached_zone_stats(entity_id)
    if cached:
        return ZoneStats(**cached)

    zone = (
        db.query(Zone)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Зона не найдена")

    details = get_zone_detailed_stats(db, entity_id)

    result = ZoneStats(
        entity_id         = zone.entity_id,
        name              = zone.name,
        zone_type         = zone.zone_type,
        pollution_index   = zone.pollution_index,
        traffic_index     = zone.traffic_index,
        risk_score        = zone.risk_score,
        **details,
    )

    # Кешируем на 10 минут
    cache_zone_stats(entity_id, result.model_dump(), ttl=600)
    return result


@router.get("/{entity_id}/problems", response_model=ProblemList)
def get_zone_problems(
    entity_id: int,
    status:    str | None = Query(None),  # noqa: F811
    offset:    int        = Query(0,  ge=0),
    limit:     int        = Query(20, ge=1, le=100),
    db:        Session    = Depends(get_db),
):
    """
    Все проблемы зоны с фильтрацией и пагинацией.
    Удобно для отображения проблем конкретного района на карте.
    """
    zone = (
        db.query(Zone)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Зона не найдена")

    query = (
        db.query(Problem)
        .filter_by(zone_entity_id=entity_id, is_current=True)
    )
    if status:
        query = query.filter(Problem.status == status)

    total    = query.count()
    problems = (
        query
        .order_by(Problem.priority_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Конвертируем через _to_public из problems роутера
    from app.api.v1.problems import _to_public
    return ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.get("/{entity_id}/children", response_model=list[ZonePublic])
def get_zone_children(entity_id: int, db: Session = Depends(get_db)):
    """
    Дочерние зоны — подрайоны.
    Например: город Бишкек → [Первомайский, Свердловский, Октябрьский, Ленинский]
    """
    children = (
        db.query(Zone)
        .filter_by(parent_entity_id=entity_id, is_current=True)
        .order_by(Zone.name)
        .all()
    )
    return children


@router.get("/{entity_id}/history", response_model=list[ZonePublic])
def get_zone_history(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_role(UserRole.admin)),
):
    """
    История версий зоны — как менялась статистика со временем.
    Только для админов — данные для аналитики и Digital Twin.
    """
    versions = (
        db.query(Zone)
        .filter_by(entity_id=entity_id)
        .order_by(Zone.version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="Зона не найдена")
    return versions


@router.post("/{entity_id}/recalculate", response_model=ZonePublic)
def recalculate_zone(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_role(UserRole.admin)),
):
    """
    Принудительный пересчёт статистики зоны.
    Обычно вызывается автоматически Celery — этот эндпоинт для ручного запуска.
    """
    zone = (
        db.query(Zone)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not zone:
        raise HTTPException(status_code=404, detail="Зона не найдена")

    updated = recalculate_zone_stats(
        db             = db,
        zone_entity_id = entity_id,
        changed_by_id  = current_user.entity_id,
    )
    return updated