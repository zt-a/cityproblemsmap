# app/api/v1/problems.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from sqlalchemy import func

from app.database import get_db
from app.models.problem import Problem, ProblemStatus
from app.models.user import User, UserRole
from app.schemas.problem import ProblemCreate, ProblemUpdate, ProblemStatusUpdate, ProblemPublic, ProblemList
from app.services.versioning import create_new_version
from app.services.geo import check_user_city
from app.api.deps import get_current_user
from app.workers.tasks_zones import update_zone_stats
from app.services.cache import (
    get_cached_problem,
    cache_problem,
    invalidate_problem_cache,
    CacheService,
)
from app.middleware.rate_limit import limiter
from app.dependencies.captcha import verify_captcha_token

router = APIRouter(prefix="/problems", tags=["problems"])


def _to_public(problem: Problem) -> ProblemPublic:
    lat, lon = None, None

    if problem.location is not None:
        try:
            # После db.refresh() location может быть WKBElement
            from geoalchemy2.shape import to_shape
            point = to_shape(problem.location)
            lon, lat = point.x, point.y
        except Exception:
            # Fallback — парсим вручную из WKB hex строки
            from shapely import wkb as shapely_wkb
            if hasattr(problem.location, 'data'):
                point = shapely_wkb.loads(problem.location.data, hex=True)
                lon, lat = point.x, point.y

    data = {
        col: getattr(problem, col)
        for col in problem.__table__.columns.keys()
        if col not in ("location",)
    }
    data["latitude"]  = lat
    data["longitude"] = lon
    data["tags"]      = problem.tags or []

    return ProblemPublic(**data)


@router.post("/", response_model=ProblemPublic, status_code=201)
@limiter.limit("20/hour")  # 20 проблем в час - защита от спама
def create_problem(
    request:      Request,
    data:         ProblemCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
    captcha_verified: bool = Depends(verify_captcha_token)
):
    """
    Создать новую проблему.
    Пользователь может добавить проблему только в своём городе.
    """

    # Проверка геолокации
    check_user_city(current_user, data.city)

    # Новый entity_id из глобального sequence
    entity_id = Problem.next_entity_id(db)

    # PostGIS POINT из координат (longitude, latitude — важен порядок!)
    location = ST_SetSRID(
        ST_MakePoint(data.longitude, data.latitude), 4326
    )

    problem = Problem(
        entity_id        = entity_id,
        version          = 1,
        is_current       = True,
        author_entity_id = current_user.entity_id,
        title            = data.title,
        description      = data.description,
        country          = data.country,
        city             = data.city,
        district         = data.district,
        address          = data.address,
        location         = location,
        problem_type     = data.problem_type,
        nature           = data.nature,
        tags             = data.tags,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    # Инвалидируем кеш списка проблем для города
    CacheService.delete_pattern(f"problems:list:{data.city}")

    # ── Celery: пересчёт статистики зоны в фоне ──────────
    # Запускается ПОСЛЕ commit — проблема уже в БД
    if problem.zone_entity_id:
        update_zone_stats.delay(
            zone_entity_id = problem.zone_entity_id,
            changed_by_id  = current_user.entity_id,
        )

    return _to_public(problem)


@router.get("/", response_model=ProblemList)
def list_problems(
    city:         str | None         = Query(None, description="Фильтр по городу"),
    problem_type: str | None         = Query(None, description="Тип проблемы"),
    status:       ProblemStatus | None = Query(None, description="Статус"),
    offset:       int                = Query(0,  ge=0),
    limit:        int                = Query(20, ge=1, le=100),
    db:           Session            = Depends(get_db),
):
    """
    Список актуальных проблем с фильтрацией и пагинацией.
    Всегда возвращает только is_current=True версии.
    """
    # Кешируем только первую страницу без фильтров (популярные проблемы)
    cache_key = None
    if offset == 0 and limit == 20 and not problem_type and not status and city:
        cache_key = f"problems:list:{city}"
        cached = CacheService.get(cache_key)
        if cached:
            return ProblemList(**cached)

    query = db.query(Problem).filter(Problem.is_current)

    if city:
        query = query.filter(
            func.lower(Problem.city) == city.lower().strip()
        )
    if problem_type:
        query = query.filter(Problem.problem_type == problem_type)
    if status:
        query = query.filter(Problem.status == status)

    total    = query.count()
    problems = (
        query
        .order_by(Problem.priority_score.desc(), Problem.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )

    # Кешируем результат на 2 минуты
    if cache_key:
        CacheService.set(cache_key, result.model_dump(), ttl=120)

    return result


@router.get("/{entity_id}", response_model=ProblemPublic)
def get_problem(entity_id: int, db: Session = Depends(get_db)):
    """Получить текущую версию проблемы по entity_id."""
    # Проверяем кеш
    cached = get_cached_problem(entity_id)
    if cached:
        return ProblemPublic(**cached)

    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    result = _to_public(problem)
    # Кешируем на 5 минут
    cache_problem(entity_id, result.model_dump(), ttl=300)
    return result


@router.get("/{entity_id}/history", response_model=list[ProblemPublic])
def get_problem_history(entity_id: int, db: Session = Depends(get_db)):
    """
    История всех версий проблемы.
    Показывает как менялся статус, описание, scores.
    """
    versions = (
        db.query(Problem)
        .filter_by(entity_id=entity_id)
        .order_by(Problem.version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="Проблема не найдена")
    return [_to_public(p) for p in versions]


@router.patch("/{entity_id}", response_model=ProblemPublic)
def update_problem(
    entity_id:    int,
    data:         ProblemUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Обновить проблему (только автор).
    Можно изменить: title, description, address, location, problem_type, tags.
    Создаёт новую версию — история изменений сохраняется.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Только автор может редактировать
    if problem.author_entity_id != current_user.entity_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только автор может редактировать проблему",
        )

    # Собираем поля для обновления
    update_fields = data.model_dump(exclude_unset=True)

    # Если обновляются координаты, создаём новый PostGIS POINT
    lat = update_fields.pop("latitude", None)
    lon = update_fields.pop("longitude", None)

    if lat is not None and lon is not None:
        update_fields["location"] = ST_SetSRID(
            ST_MakePoint(lon, lat), 4326
        )
    elif lat is not None or lon is not None:
        # Если передана только одна координата, получаем вторую из текущей проблемы
        from geoalchemy2.shape import to_shape
        point = to_shape(problem.location)
        current_lon, current_lat = point.x, point.y

        final_lat = lat if lat is not None else current_lat
        final_lon = lon if lon is not None else current_lon

        update_fields["location"] = ST_SetSRID(
            ST_MakePoint(final_lon, final_lat), 4326
        )

    if not update_fields:
        # Нет изменений
        return _to_public(problem)

    updated = create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "problem_updated",
        **update_fields,
    )

    # Инвалидируем кеш проблемы и списка
    invalidate_problem_cache(entity_id)
    CacheService.delete_pattern(f"problems:list:{updated.city}")

    return _to_public(updated)


@router.patch("/{entity_id}/status", response_model=ProblemPublic)
def update_status(
    entity_id:    int,
    data:         ProblemStatusUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Обновить статус проблемы.
    - Автор может закрыть свою проблему
    - Модератор/админ/official может менять любой статус
    Создаёт новую версию — история статусов сохраняется.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверка прав
    is_author = problem.author_entity_id == current_user.entity_id
    is_privileged = current_user.role in (
        UserRole.admin, UserRole.moderator, UserRole.official
    )

    if not is_author and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на изменение статуса",
        )

    fields = {"status": data.status}
    if data.resolution_note:
        fields["resolution_note"] = data.resolution_note
    if data.status == ProblemStatus.solved:
        from datetime import datetime, timezone
        fields["resolved_by_entity_id"] = current_user.entity_id
        fields["resolved_at"]           = datetime.now(timezone.utc)

    updated = create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"status_update_to_{data.status}",
        **fields,
    )

    # Инвалидируем кеш проблемы и списка
    invalidate_problem_cache(entity_id)
    CacheService.delete_pattern(f"problems:list:{updated.city}")

    # ── Celery: пересчёт статистики зоны в фоне ──────────
    # Статус изменился — зона должна обновить счётчики
    if updated.zone_entity_id:
        update_zone_stats.delay(
            zone_entity_id = updated.zone_entity_id,
            changed_by_id  = current_user.entity_id,
        )
    # ─────────────────────────────────────────────────────
    return _to_public(updated)