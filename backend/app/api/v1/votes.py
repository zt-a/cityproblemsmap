# app/api/v1/votes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vote import Vote
from app.models.problem import Problem
from app.models.user import User
from app.schemas.vote import VoteCreate, VotePublic, VoteStats
from app.services.versioning import create_new_version
from app.api.deps import get_current_user
from app.services.cache import invalidate_problem_cache
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/problems", tags=["votes"])
# prefix="/problems" чтобы URL был /problems/{id}/votes — логично


@router.post("/{problem_entity_id}/votes", response_model=VotePublic, status_code=201)
@limiter.limit("50/hour")  # 50 голосов в час - защита от накрутки
def cast_vote(
    request:           Request,
    problem_entity_id: int,
    data:              VoteCreate,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Проголосовать за проблему.

    Если пользователь уже голосовал — старый голос помечается
    is_current=False, создаётся новая версия голоса.
    После голоса пересчитываются scores проблемы.
    """

    # Валидация — хотя бы одно поле должно быть заполнено
    if data.is_empty():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заполни хотя бы одно поле голосования",
        )

    # Проверить что проблема существует
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Автор не может голосовать за свою проблему
    if problem.author_entity_id == current_user.entity_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя голосовать за свою проблему",
        )

    # Проверить есть ли уже голос от этого пользователя
    existing_vote = (
        db.query(Vote)
        .filter_by(
            problem_entity_id = problem_entity_id,
            user_entity_id    = current_user.entity_id,
            is_current        = True,
        )
        .first()
    )

    if existing_vote:
        # Голос уже есть — создаём новую версию с изменёнными полями
        # Незаполненные поля берём из предыдущего голоса (merge)
        merged = {
            "is_true":       data.is_true       if data.is_true       is not None else existing_vote.is_true,
            "urgency":       data.urgency       if data.urgency       is not None else existing_vote.urgency,
            "impact":        data.impact        if data.impact        is not None else existing_vote.impact,
            "inconvenience": data.inconvenience if data.inconvenience is not None else existing_vote.inconvenience,
        }
        vote = create_new_version(
            db            = db,
            model_class   = Vote,
            entity_id     = existing_vote.entity_id,
            changed_by_id = current_user.entity_id,
            change_reason = "vote_changed",
            **merged,
        )
    else:
        # Первый голос — INSERT новой записи
        entity_id = Vote.next_entity_id(db)

        # Вес голоса = репутация пользователя (снэпшот)
        # Минимум 1.0, растёт с репутацией
        weight = max(1.0, 1.0 + current_user.reputation * 0.1)

        vote = Vote(
            entity_id         = entity_id,
            version           = 1,
            is_current        = True,
            problem_entity_id = problem_entity_id,
            user_entity_id    = current_user.entity_id,
            is_true           = data.is_true,
            urgency           = data.urgency,
            impact            = data.impact,
            inconvenience     = data.inconvenience,
            weight            = round(weight, 4),
        )
        db.add(vote)
        db.commit()
        db.refresh(vote)

    # Пересчитать scores проблемы и создать новую её версию
    try:
        from app.services.scoring import recalculate_scores
        recalculate_scores(
            db                = db,
            problem_entity_id = problem_entity_id,
            changed_by_id     = current_user.entity_id,
        )
    except Exception:
        # Redis недоступен (локальная разработка/тесты) — считаем синхронно
        from app.services.scoring import recalculate_scores
        recalculate_scores(
            db                = db,
            problem_entity_id = problem_entity_id,
            changed_by_id     = current_user.entity_id,
        )

    invalidate_problem_cache(problem_entity_id)

    # Отправить WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="vote_changed",
            data={
                "vote_count": problem.vote_count + 1 if not existing_vote else problem.vote_count,
                "user_id": current_user.entity_id,
            }
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to broadcast vote update: {e}")

    return vote


@router.get("/{problem_entity_id}/votes/my", response_model=VotePublic)
def get_my_vote(
    problem_entity_id: int,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """Получить свой текущий голос по проблеме."""
    vote = (
        db.query(Vote)
        .filter_by(
            problem_entity_id = problem_entity_id,
            user_entity_id    = current_user.entity_id,
            is_current        = True,
        )
        .first()
    )
    if not vote:
        raise HTTPException(status_code=404, detail="Ты ещё не голосовал")
    return vote


@router.get("/{problem_entity_id}/votes/stats", response_model=VoteStats)
def get_vote_stats(
    problem_entity_id: int,
    db:                Session = Depends(get_db),
):
    """
    Агрегированная статистика голосов по проблеме.
    Берётся из scores проблемы — не считается каждый раз заново.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Считаем true/fake для отображения
    votes = (
        db.query(Vote)
        .filter_by(problem_entity_id=problem_entity_id, is_current=True)
        .all()
    )
    truth_votes = [v for v in votes if v.is_true is not None]
    true_count  = sum(1 for v in truth_votes if v.is_true)
    fake_count  = sum(1 for v in truth_votes if not v.is_true)

    return VoteStats(
        total_votes         = problem.vote_count,
        true_count          = true_count,
        fake_count          = fake_count,
        truth_score         = problem.truth_score,
        urgency_score       = problem.urgency_score,
        impact_score        = problem.impact_score,
        inconvenience_score = problem.inconvenience_score,
        priority_score      = problem.priority_score,
    )


@router.delete("/{problem_entity_id}/votes/my", status_code=204)
@limiter.limit("20/hour")  # 20 удалений в час
def delete_my_vote(
    request:           Request,
    problem_entity_id: int,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Удалить свой голос (отменить голосование).

    На самом деле создаёт новую версию голоса с is_current=False,
    чтобы сохранить историю в append-only архитектуре.
    """

    # Найти текущий голос пользователя
    existing_vote = (
        db.query(Vote)
        .filter_by(
            problem_entity_id = problem_entity_id,
            user_entity_id    = current_user.entity_id,
            is_current        = True,
        )
        .first()
    )

    if not existing_vote:
        raise HTTPException(
            status_code=404,
            detail="Голос не найден - ты ещё не голосовал"
        )

    # Пометить текущий голос как неактуальный
    # Это единственный UPDATE в системе
    from datetime import datetime, timezone
    existing_vote.is_current = False
    existing_vote.superseded_at = datetime.now(timezone.utc)

    db.commit()

    # Пересчитать scores проблемы
    try:
        from app.services.scoring import recalculate_scores
        recalculate_scores(
            db                = db,
            problem_entity_id = problem_entity_id,
            changed_by_id     = current_user.entity_id,
        )
    except Exception:
        from app.services.scoring import recalculate_scores
        recalculate_scores(
            db                = db,
            problem_entity_id = problem_entity_id,
            changed_by_id     = current_user.entity_id,
        )

    invalidate_problem_cache(problem_entity_id)

    # Отправить WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="vote_deleted",
            data={
                "user_id": current_user.entity_id,
            }
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to broadcast vote deletion: {e}")

    return None


@router.get("/{problem_entity_id}/votes/history", response_model=list[VotePublic])
def get_votes_history(
    problem_entity_id: int,
    db:                Session = Depends(get_db),
):
    """
    Полная история всех голосов включая изменённые.
    Только для аналитики и AI — обычным пользователям не нужно.
    """
    votes = (
        db.query(Vote)
        .filter_by(problem_entity_id=problem_entity_id)
        .order_by(Vote.entity_id, Vote.version)
        .all()
    )
    if not votes:
        raise HTTPException(status_code=404, detail="Голосов нет")
    return votes