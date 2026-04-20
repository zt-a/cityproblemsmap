# app/api/v1/moderator.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User, UserStatus
from app.models.problem import Problem, ProblemStatus
from app.models.comment import Comment
from app.schemas.moderator import (
    FlaggedCommentList, 
    SuspiciousProblemList, SuspiciousProblem,
    VerifyProblemRequest, HideCommentRequest,
    ModeratorStats,
)
from app.schemas.problem import ProblemPublic, ProblemList
from app.services.versioning import create_new_version
from app.api.deps import get_moderator
from app.api.v1.problems import _to_public

router = APIRouter(prefix="/moderator", tags=["moderator"])


# ══════════════════════════════════════════════════════════
# КОММЕНТАРИИ С ЖАЛОБАМИ
# ══════════════════════════════════════════════════════════

@router.get("/comments/flagged", response_model=FlaggedCommentList)
def get_flagged_comments(
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Комментарии с жалобами от пользователей.
    Требуют проверки модератором.
    """
    query = (
        db.query(Comment)
        .filter_by(is_current=True, is_flagged=True)
        .order_by(Comment.created_at.desc())
    )

    total    = query.count()
    comments = query.offset(offset).limit(limit).all()

    return FlaggedCommentList(
        items  = comments,
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.post("/comments/{entity_id}/hide")
def hide_comment(
    entity_id:    int,
    data:         HideCommentRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Скрыть комментарий нарушающий правила.
    Комментарий остаётся в БД но помечается как скрытый.
    """
    comment = (
        db.query(Comment)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    # Добавляем поле для скрытых комментариев через change_reason
    updated = create_new_version(
        db            = db,
        model_class   = Comment,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"hidden_by_moderator: {data.reason}",
        is_flagged    = True,
        flag_reason   = data.reason,
    )

    # Уведомить автора комментария
    try:
        from app.services.notification_service import NotificationService
        NotificationService.notify_comment_hidden(
            db=db,
            comment=comment,
            reason=data.reason,
            actor_entity_id=current_user.entity_id,
        )
    except Exception as e:
        import logging
        logging.warning(f"Failed to create notification: {e}")

    return {"message": "Комментарий скрыт", "entity_id": updated.entity_id}


@router.post("/comments/{entity_id}/restore")
def restore_comment(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Восстановить скрытый комментарий.
    Снимает флаг и причину жалобы.
    """
    comment = (
        db.query(Comment)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if not comment.is_flagged:
        raise HTTPException(
            status_code=400,
            detail="Комментарий не был скрыт",
        )

    updated = create_new_version(
        db            = db,
        model_class   = Comment,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "restored_by_moderator",
        is_flagged    = False,
        flag_reason   = None,
    )

    return {"message": "Комментарий восстановлен", "entity_id": updated.entity_id}


# ══════════════════════════════════════════════════════════
# ПОДОЗРИТЕЛЬНЫЕ ПРОБЛЕМЫ
# ══════════════════════════════════════════════════════════

@router.get("/problems/suspicious", response_model=SuspiciousProblemList)
def get_suspicious_problems(
    threshold:    float   = Query(0.3, ge=0.0, le=1.0, description="Порог truth_score"),
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Проблемы с низким truth_score — возможно фейки.
    По умолчанию показывает проблемы с truth_score < 0.3.
    """
    query = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.open,
            Problem.truth_score < threshold,
            Problem.vote_count >= 3,  # минимум 3 голоса для оценки
        )
        .order_by(Problem.truth_score.asc())
    )

    total    = query.count()
    problems = query.offset(offset).limit(limit).all()

    items = [
        SuspiciousProblem(
            entity_id=p.entity_id,
            title=p.title,
            city=p.city,
            author_entity_id=p.author_entity_id,
            truth_score=p.truth_score,
            vote_count=p.vote_count,
            status=p.status.value,
            created_at=p.created_at,
        )
        for p in problems
    ]

    return SuspiciousProblemList(
        items  = items,
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.get("/problems/pending", response_model=ProblemList)
def get_pending_problems(
    hours:        int     = Query(168, ge=1, le=720, description="Проблемы за последние N часов"),
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Новые проблемы требующие модерации (статус pending).
    Модератор должен одобрить или отклонить.
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    query = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.pending,  # Только pending проблемы
            Problem.created_at >= cutoff_time,
        )
        .order_by(Problem.created_at.desc())
    )

    total    = query.count()
    problems = query.offset(offset).limit(limit).all()

    return ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.post("/problems/{entity_id}/verify", response_model=ProblemPublic)
def verify_problem(
    entity_id:    int,
    data:         VerifyProblemRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Подтвердить проблему как валидную.
    Модератор проверил и подтверждает что проблема реальна.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    note = data.note or "Проверено модератором"

    updated = create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"verified_by_moderator: {note}",
        status        = ProblemStatus.open,  # Одобренная проблема становится open
    )

    # Уведомить автора о подтверждении
    try:
        from app.services.notification_service import NotificationService
        NotificationService.notify_problem_verified(
            db=db,
            problem=problem,
            actor_entity_id=current_user.entity_id,
        )
    except Exception as e:
        import logging
        logging.warning(f"Failed to create notification: {e}")

    return _to_public(updated)


# ══════════════════════════════════════════════════════════
# СТАТИСТИКА МОДЕРАТОРА
# ══════════════════════════════════════════════════════════

@router.get("/stats", response_model=ModeratorStats)
def get_moderator_stats(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Статистика работы текущего модератора.
    Показывает сколько проблем проверено, комментариев скрыто и т.д.
    """
    moderator_id = current_user.entity_id

    # Подтверждённые проблемы
    problems_verified = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.changed_by_id == moderator_id,
            Problem.change_reason.like("verified_by_moderator%"),
        )
        .count()
    )

    # Отклонённые проблемы
    problems_rejected = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.rejected,
            Problem.changed_by_id == moderator_id,
        )
        .count()
    )

    # Скрытые комментарии
    comments_hidden = (
        db.query(Comment)
        .filter(
            Comment.is_current,
            Comment.is_flagged,
            Comment.changed_by_id == moderator_id,
            Comment.change_reason.like("hidden_by_moderator%"),
        )
        .count()
    )

    # Заблокированные пользователи
    users_suspended = (
        db.query(User)
        .filter(
            User.is_current,
            User.status == UserStatus.suspended,
            User.changed_by_id == moderator_id,
        )
        .count()
    )

    # Жалобы на рассмотрении
    flagged_pending = (
        db.query(Comment)
        .filter_by(is_current=True, is_flagged=True)
        .count()
    )

    # Подозрительные проблемы
    suspicious_pending = (
        db.query(Problem)
        .filter(
            Problem.is_current,
            Problem.status == ProblemStatus.open,
            Problem.truth_score < 0.3,
            Problem.vote_count >= 3,
        )
        .count()
    )

    return ModeratorStats(
        problems_verified  = problems_verified,
        problems_rejected  = problems_rejected,
        comments_hidden    = comments_hidden,
        users_suspended    = users_suspended,
        flagged_pending    = flagged_pending,
        suspicious_pending = suspicious_pending,
    )
