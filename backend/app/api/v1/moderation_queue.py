# app/api/v1/moderation_queue.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User, UserRole
from app.models.problem import Problem, ProblemStatus
from app.models.comment import Comment
from app.models.report import Report
from app.api.deps import require_role
from app.schemas.problem import ProblemPublic
from app.schemas.comment import CommentPublic
from app.services.versioning import read_with_custom_filters, count_with_custom_filters

router = APIRouter(prefix="/moderation/queue", tags=["moderation-queue"])


@router.get("/problems", response_model=List[ProblemPublic])
def get_problems_queue(
    status: Optional[str] = Query(None, description="Фильтр по статусу: pending, flagged"),
    priority: Optional[str] = Query(None, description="Приоритет: high, medium, low"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin]))
):
    """
    Получить очередь проблем для модерации.

    Показывает:
    - Новые проблемы (pending)
    - Проблемы с жалобами (flagged)
    - Проблемы требующие внимания
    """

    custom_filters = []

    # Фильтр по статусу
    if status == "pending":
        custom_filters.append(Problem.status == ProblemStatus.PENDING)
    elif status == "flagged":
        # Проблемы с активными жалобами
        flagged_ids = (
            db.query(Report.target_entity_id)
            .filter(
                Report.target_type == "problem",
                Report.is_current,
                Report.status == "pending"
            )
            .subquery()
        )
        custom_filters.append(Problem.entity_id.in_(flagged_ids))
        custom_filters.append(Problem.status != ProblemStatus.REJECTED)

    # Приоритет (по количеству жалоб и времени)
    if priority == "high":
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        high_report_ids = (
            db.query(Report.target_entity_id)
            .filter(
                Report.target_type == "problem",
                Report.is_current
            )
            .group_by(Report.target_entity_id)
            .having(func.count(Report.id) >= 3)
            .subquery()
        )

        custom_filters.append(
            or_(
                Problem.created_at < week_ago,
                Problem.entity_id.in_(high_report_ids)
            )
        )

    # Использовать метод из versioning.py
    problems = read_with_custom_filters(
        db=db,
        model_class=Problem,
        custom_filters=custom_filters,
        order_by=Problem.created_at.asc(),
        limit=limit,
        offset=offset
    )

    # Конвертация в PublicSchema
    result = []
    for problem in problems:
        from app.api.v1.problems import _to_public
        result.append(_to_public(problem))

    return result


@router.get("/comments", response_model=List[CommentPublic])
def get_comments_queue(
    status: Optional[str] = Query(None, description="Фильтр: flagged"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin]))
):
    """
    Получить очередь комментариев для модерации.

    Показывает комментарии с жалобами.
    """

    custom_filters = []

    # Только комментарии с жалобами
    if status == "flagged" or status is None:
        flagged_comment_ids = (
            db.query(Report.target_entity_id)
            .filter(
                Report.target_type == "comment",
                Report.is_current,
                Report.status == "pending"
            )
            .subquery()
        )
        custom_filters.append(Comment.entity_id.in_(flagged_comment_ids))

    # Использовать метод из versioning.py
    comments = read_with_custom_filters(
        db=db,
        model_class=Comment,
        custom_filters=custom_filters,
        order_by=Comment.created_at.asc(),
        limit=limit,
        offset=offset
    )

    return [CommentPublic.model_validate(c) for c in comments]


@router.get("/stats")
def get_moderation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin]))
):
    """
    Статистика очереди модерации.
    """

    # Проблемы в статусе pending
    pending_problems = count_with_custom_filters(
        db=db,
        model_class=Problem,
        custom_filters=[Problem.status == ProblemStatus.PENDING]
    )

    # Проблемы с жалобами
    flagged_problem_ids = (
        db.query(func.count(func.distinct(Report.target_entity_id)))
        .filter(
            Report.target_type == "problem",
            Report.is_current,
            Report.status == "pending"
        )
        .scalar()
    )

    # Комментарии с жалобами
    flagged_comment_ids = (
        db.query(func.count(func.distinct(Report.target_entity_id)))
        .filter(
            Report.target_type == "comment",
            Report.is_current,
            Report.status == "pending"
        )
        .scalar()
    )

    # Проблемы старше 7 дней без модерации
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    old_pending = count_with_custom_filters(
        db=db,
        model_class=Problem,
        custom_filters=[
            Problem.status == ProblemStatus.PENDING,
            Problem.created_at < week_ago
        ]
    )

    return {
        "pending_problems": pending_problems,
        "flagged_problems": flagged_problem_ids or 0,
        "flagged_comments": flagged_comment_ids or 0,
        "old_pending_problems": old_pending,
        "total_queue": pending_problems + (flagged_problem_ids or 0) + (flagged_comment_ids or 0)
    }
