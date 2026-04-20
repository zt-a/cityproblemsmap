# app/api/v1/reports.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.models.problem import Problem
from app.models.comment import Comment
from app.models.user import User, UserRole
from app.schemas.report import ReportCreate, ReportResolve, ReportPublic, ReportList
from app.api.deps import get_current_user, require_role
from app.services.versioning import create_new_version

router = APIRouter(prefix="/reports", tags=["reports"])


def _check_target_exists(db: Session, target_type: str, target_entity_id: int):
    """Проверяет существование цели жалобы"""
    if target_type == "problem":
        target = db.query(Problem).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Проблема не найдена")
    elif target_type == "comment":
        target = db.query(Comment).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
    elif target_type == "user":
        target = db.query(User).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    else:
        raise HTTPException(status_code=400, detail="Неверный тип цели")


@router.post("/", response_model=ReportPublic, status_code=201)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать жалобу на проблему, комментарий или пользователя.
    Доступно всем авторизованным пользователям.
    """
    # Проверяем существование цели
    _check_target_exists(db, data.target_type, data.target_entity_id)

    # Проверяем что пользователь не жалуется на самого себя
    if data.target_type == "user" and data.target_entity_id == current_user.entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя пожаловаться на самого себя",
        )

    # Проверяем дубликаты (один пользователь может пожаловаться только один раз)
    existing = (
        db.query(Report)
        .filter_by(
            reporter_entity_id=current_user.entity_id,
            target_type=data.target_type,
            target_entity_id=data.target_entity_id,
            is_current=True,
        )
        .filter(Report.status.in_(["pending", "reviewed"]))
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже пожаловались на этот объект",
        )

    entity_id = Report.next_entity_id(db)

    report = Report(
        entity_id=entity_id,
        version=1,
        is_current=True,
        reporter_entity_id=current_user.entity_id,
        target_type=data.target_type,
        target_entity_id=data.target_entity_id,
        reason=data.reason,
        description=data.description,
        status="pending",
        changed_by_id=current_user.entity_id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get("/my", response_model=ReportList)
def get_my_reports(
    status_filter: str | None = Query(None, description="Фильтр по статусу"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить свои жалобы"""
    query = db.query(Report).filter_by(
        reporter_entity_id=current_user.entity_id,
        is_current=True,
    )

    if status_filter:
        query = query.filter_by(status=status_filter)

    total = query.count()
    reports = (
        query
        .order_by(Report.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return ReportList(
        items=reports,
        total=total,
        offset=offset,
        limit=limit,
    )


# ── Endpoints для модераторов ──────────────────────────────


@router.get("/moderation/queue", response_model=ReportList)
def get_moderation_queue(
    status_filter: str | None = Query(None, description="Фильтр по статусу"),
    target_type: str | None = Query(None, description="Фильтр по типу цели"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Очередь модерации жалоб.
    Доступно только модераторам и админам.
    Показывает только reports на существующие объекты.
    Использует SQL JOIN для гарантии валидности.
    """
    from sqlalchemy import and_, or_

    # Базовый query с JOIN для проверки существования target
    query = db.query(Report).filter_by(is_current=True)

    # Фильтруем по типу target и проверяем существование через JOIN
    if target_type:
        if target_type == "problem":
            query = query.join(
                Problem,
                and_(
                    Report.target_entity_id == Problem.entity_id,
                    Problem.is_current == True
                )
            )
        elif target_type == "comment":
            query = query.join(
                Comment,
                and_(
                    Report.target_entity_id == Comment.entity_id,
                    Comment.is_current == True
                )
            )
        elif target_type == "user":
            query = query.join(
                User,
                and_(
                    Report.target_entity_id == User.entity_id,
                    User.is_current == True
                )
            )
        query = query.filter_by(target_type=target_type)
    else:
        # Если target_type не указан, проверяем все типы через LEFT JOIN
        # Используем subquery для проверки существования
        from sqlalchemy import exists, select

        problem_exists = exists(select(1).where(
            and_(
                Problem.entity_id == Report.target_entity_id,
                Problem.is_current == True,
                Report.target_type == "problem"
            )
        ))

        comment_exists = exists(select(1).where(
            and_(
                Comment.entity_id == Report.target_entity_id,
                Comment.is_current == True,
                Report.target_type == "comment"
            )
        ))

        user_exists = exists(select(1).where(
            and_(
                User.entity_id == Report.target_entity_id,
                User.is_current == True,
                Report.target_type == "user"
            )
        ))

        # Показываем только reports где target существует
        query = query.filter(
            or_(problem_exists, comment_exists, user_exists)
        )

    if status_filter:
        query = query.filter_by(status=status_filter)
    else:
        # По умолчанию показываем только pending и reviewed
        query = query.filter(Report.status.in_(["pending", "reviewed"]))

    total = query.count()
    reports = (
        query
        .order_by(Report.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Добавляем problem_entity_id для comment reports
    items = []
    for report in reports:
        report_dict = {
            "entity_id": report.entity_id,
            "version": report.version,
            "is_current": report.is_current,
            "created_at": report.created_at,
            "reporter_entity_id": report.reporter_entity_id,
            "target_type": report.target_type,
            "target_entity_id": report.target_entity_id,
            "reason": report.reason,
            "description": report.description,
            "status": report.status,
            "resolved_by_entity_id": report.resolved_by_entity_id,
            "resolution_note": report.resolution_note,
            "problem_entity_id": None,
        }

        # Для comment reports находим problem_entity_id
        if report.target_type == "comment":
            comment = db.query(Comment).filter_by(
                entity_id=report.target_entity_id,
                is_current=True
            ).first()
            if comment:
                report_dict["problem_entity_id"] = comment.problem_entity_id

        items.append(ReportPublic(**report_dict))

    return ReportList(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.patch("/moderation/{entity_id}/resolve", response_model=ReportPublic)
def resolve_report(
    entity_id: int,
    data: ReportResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Разрешить жалобу (принять или отклонить).
    Доступно только модераторам и админам.
    """
    report = (
        db.query(Report)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Жалоба не найдена")

    if report.status in ["resolved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Жалоба уже обработана",
        )

    if data.status not in ["resolved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Статус должен быть resolved или rejected",
        )

    updated = create_new_version(
        db=db,
        model_class=Report,
        entity_id=entity_id,
        changed_by_id=current_user.entity_id,
        change_reason=f"report_{data.status}",
        status=data.status,
        resolved_by_entity_id=current_user.entity_id,
        resolution_note=data.resolution_note,
    )

    return updated


@router.get("/moderation/stats")
def get_moderation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Статистика жалоб для модераторов.
    """
    pending_count = (
        db.query(Report)
        .filter_by(is_current=True, status="pending")
        .count()
    )

    reviewed_count = (
        db.query(Report)
        .filter_by(is_current=True, status="reviewed")
        .count()
    )

    resolved_count = (
        db.query(Report)
        .filter_by(is_current=True, status="resolved")
        .count()
    )

    rejected_count = (
        db.query(Report)
        .filter_by(is_current=True, status="rejected")
        .count()
    )

    # Статистика по типам целей
    from sqlalchemy import func
    by_target_type = (
        db.query(
            Report.target_type,
            func.count(Report.id).label("count")
        )
        .filter_by(is_current=True, status="pending")
        .group_by(Report.target_type)
        .all()
    )

    return {
        "pending": pending_count,
        "reviewed": reviewed_count,
        "resolved": resolved_count,
        "rejected": rejected_count,
        "by_target_type": {item[0]: item[1] for item in by_target_type},
    }
