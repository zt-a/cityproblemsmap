# app/api/v1/official.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.problem import Problem, ProblemStatus, ResolverType
from app.models.comment import Comment
from app.models.zone import Zone
from app.schemas.official import (
    AssignedProblemList, AssignedProblem,
    TakeProblemRequest, ResolveProblemRequest,
    OfficialCommentRequest, OfficialZone,
    OfficialStats,
)
from app.schemas.problem import ProblemPublic
from app.services.versioning import create_new_version
from app.api.deps import get_official
from app.api.v1.problems import _to_public

router = APIRouter(prefix="/official", tags=["official"])


# ══════════════════════════════════════════════════════════
# ПРОБЛЕМЫ НАЗНАЧЕННЫЕ НА ОФИЦИАЛА
# ══════════════════════════════════════════════════════════

@router.get("/problems/assigned", response_model=AssignedProblemList)
def get_assigned_problems(
    status:       ProblemStatus | None = Query(None),
    offset:       int                  = Query(0,  ge=0),
    limit:        int                  = Query(20, ge=1, le=100),
    db:           Session              = Depends(get_db),
    current_user: User                 = Depends(get_official),
):
    """
    Проблемы назначенные на текущего официала.
    Показывает проблемы где resolved_by_entity_id = текущий пользователь
    или проблемы в зонах закреплённых за официалом.
    """
    official_id = current_user.entity_id

    # Получаем зоны официала (можно расширить логику через отдельную таблицу)
    # Пока показываем проблемы где официал уже взял в работу
    query = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.resolved_by_entity_id == official_id,
        )
    )

    if status:
        query = query.filter(Problem.status == status)

    query = query.order_by(Problem.priority_score.desc())

    total    = query.count()
    problems = query.offset(offset).limit(limit).all()

    items = []
    for p in problems:
        lat, lon = None, None
        if p.location:
            try:
                from geoalchemy2.shape import to_shape
                point = to_shape(p.location)
                lon, lat = point.x, point.y
            except Exception:
                from shapely import wkb as shapely_wkb
                if hasattr(p.location, 'data'):
                    point = shapely_wkb.loads(p.location.data, hex=True)
                    lon, lat = point.x, point.y

        items.append(
            AssignedProblem(
                entity_id=p.entity_id,
                title=p.title,
                description=p.description,
                city=p.city,
                district=p.district,
                address=p.address,
                problem_type=p.problem_type,
                status=p.status,
                priority_score=p.priority_score,
                created_at=p.created_at,
                latitude=lat,
                longitude=lon,
            )
        )

    return AssignedProblemList(
        items  = items,
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.get("/problems/in-progress", response_model=AssignedProblemList)
def get_in_progress_problems(
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Проблемы в работе у текущего официала.
    Статус in_progress и назначены на официала.
    """
    official_id = current_user.entity_id

    query = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.in_progress,
            Problem.resolved_by_entity_id == official_id,
        )
        .order_by(Problem.priority_score.desc())
    )

    total    = query.count()
    problems = query.offset(offset).limit(limit).all()

    items = []
    for p in problems:
        lat, lon = None, None
        if p.location:
            try:
                from geoalchemy2.shape import to_shape
                point = to_shape(p.location)
                lon, lat = point.x, point.y
            except Exception:
                from shapely import wkb as shapely_wkb
                if hasattr(p.location, 'data'):
                    point = shapely_wkb.loads(p.location.data, hex=True)
                    lon, lat = point.x, point.y

        items.append(
            AssignedProblem(
                entity_id=p.entity_id,
                title=p.title,
                description=p.description,
                city=p.city,
                district=p.district,
                address=p.address,
                problem_type=p.problem_type,
                status=p.status,
                priority_score=p.priority_score,
                created_at=p.created_at,
                latitude=lat,
                longitude=lon,
            )
        )

    return AssignedProblemList(
        items  = items,
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.post("/problems/{entity_id}/take", response_model=ProblemPublic)
def take_problem(
    entity_id:    int,
    data:         TakeProblemRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Взять проблему в работу.
    Официал назначает себя ответственным и меняет статус на in_progress.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    if problem.status not in [ProblemStatus.open, ProblemStatus.in_progress]:
        raise HTTPException(
            status_code=400,
            detail="Можно взять только открытую проблему",
        )

    if problem.resolved_by_entity_id and problem.resolved_by_entity_id != current_user.entity_id:
        raise HTTPException(
            status_code=400,
            detail="Проблема уже назначена на другого официала",
        )

    note = data.note or "Взято в работу официальной службой"

    updated = create_new_version(
        db                    = db,
        model_class           = Problem,
        entity_id             = entity_id,
        changed_by_id         = current_user.entity_id,
        change_reason         = f"taken_by_official: {note}",
        status                = ProblemStatus.in_progress,
        resolved_by_entity_id = current_user.entity_id,
        resolver_type         = ResolverType.official_org,
    )

    return _to_public(updated)


@router.post("/problems/{entity_id}/resolve", response_model=ProblemPublic)
def resolve_problem(
    entity_id:    int,
    data:         ResolveProblemRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Отметить проблему решённой с отчётом о выполненных работах.
    Только официал назначенный на проблему может её закрыть.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    if problem.resolved_by_entity_id != current_user.entity_id:
        raise HTTPException(
            status_code=403,
            detail="Только назначенный официал может закрыть проблему",
        )

    if problem.status == ProblemStatus.solved:
        raise HTTPException(
            status_code=400,
            detail="Проблема уже решена",
        )

    updated = create_new_version(
        db              = db,
        model_class     = Problem,
        entity_id       = entity_id,
        changed_by_id   = current_user.entity_id,
        change_reason   = "resolved_by_official",
        status          = ProblemStatus.solved,
        resolved_at     = datetime.now(timezone.utc),
        resolution_note = data.resolution_note,
    )

    return _to_public(updated)


@router.post("/problems/{entity_id}/comment")
def add_official_comment(
    entity_id:    int,
    data:         OfficialCommentRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Добавить официальный ответ от городских служб.
    Комментарий помечается как official_response.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    entity_id_comment = Comment.next_entity_id(db)

    comment = Comment(
        entity_id         = entity_id_comment,
        version           = 1,
        is_current        = True,
        problem_entity_id = entity_id,
        author_entity_id  = current_user.entity_id,
        content           = data.content,
        comment_type      = "official_response",
    )

    db.add(comment)

    # Обновляем счётчик комментариев в проблеме
    create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "official_comment_added",
        comment_count = problem.comment_count + 1,
    )

    db.commit()
    db.refresh(comment)

    return {
        "message": "Официальный ответ добавлен",
        "comment_entity_id": comment.entity_id,
    }


# ══════════════════════════════════════════════════════════
# ЗОНЫ ОФИЦИАЛА
# ══════════════════════════════════════════════════════════

@router.get("/zones", response_model=list[OfficialZone])
def get_official_zones(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Зоны закреплённые за официалом.
    Показывает зоны города официала с статистикой проблем.
    """
    # Пока показываем все зоны города официала
    # В будущем можно добавить таблицу official_zones для точного назначения
    if not current_user.city:
        return []

    zones = (
        db.query(Zone)
        .filter(
            Zone.is_current,
            Zone.city == current_user.city,
        )
        .order_by(Zone.open_problems.desc())
        .all()
    )

    return [
        OfficialZone(
            entity_id=z.entity_id,
            name=z.name,
            zone_type=z.zone_type,
            city=z.city,
            total_problems=z.total_problems,
            open_problems=z.open_problems,
            solved_problems=z.solved_problems,
        )
        for z in zones
    ]


# ══════════════════════════════════════════════════════════
# СТАТИСТИКА ОФИЦИАЛА
# ══════════════════════════════════════════════════════════

@router.get("/stats", response_model=OfficialStats)
def get_official_stats(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_official),
):
    """
    Статистика работы текущего официала.
    Показывает сколько проблем назначено, решено, среднее время решения.
    """
    official_id = current_user.entity_id

    # Назначено проблем
    problems_assigned = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.resolved_by_entity_id == official_id,
        )
        .count()
    )

    # В работе
    problems_in_progress = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.in_progress,
            Problem.resolved_by_entity_id == official_id,
        )
        .count()
    )

    # Решено
    problems_resolved = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.solved,
            Problem.resolved_by_entity_id == official_id,
        )
        .count()
    )

    # Среднее время решения (в днях)
    avg_resolution_days = None
    resolved_problems = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.solved,
            Problem.resolved_by_entity_id == official_id,
            Problem.resolved_at.isnot(None),
        )
        .all()
    )

    if resolved_problems:
        total_days = 0
        for p in resolved_problems:
            if p.resolved_at and p.created_at:
                delta = p.resolved_at - p.created_at
                total_days += delta.total_seconds() / 86400  # секунды в дни

        avg_resolution_days = round(total_days / len(resolved_problems), 1)

    # Зоны под управлением
    zones_managed = (
        db.query(Zone)
        .filter(
            Zone.is_current,
            Zone.city == current_user.city,
        )
        .count()
    ) if current_user.city else 0

    # Официальных ответов
    official_responses = (
        db.query(Comment)
        .filter(
            Comment.is_current,
            Comment.author_entity_id == official_id,
            Comment.comment_type == "official_response",
        )
        .count()
    )

    return OfficialStats(
        problems_assigned    = problems_assigned,
        problems_in_progress = problems_in_progress,
        problems_resolved    = problems_resolved,
        avg_resolution_days  = avg_resolution_days,
        zones_managed        = zones_managed,
        official_responses   = official_responses,
    )
