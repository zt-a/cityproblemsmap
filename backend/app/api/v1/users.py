# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserStatus
from app.models.problem import Problem, ProblemStatus
from app.models.vote import Vote
from app.models.comment import Comment
from app.models.reputation import ReputationLog
from app.schemas.user import (
    UserPublic, UpdateProfileRequest,
    UpdateEmailRequest, ReputationHistory,
)
from app.schemas.problem import ProblemList
from app.schemas.vote import VotePublic
from app.schemas.comment import CommentPublic
from app.services.versioning import create_new_version
from app.services.auth import verify_password, get_user_by_email
from app.api.deps import get_current_user
from app.api.v1.problems import _to_public

router = APIRouter(prefix="/users", tags=["users"])


# ── Текущий пользователь ──────────────────────────────────

@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    """Текущий авторизованный пользователь."""
    return current_user


@router.patch("/me/profile", response_model=UserPublic)
def update_profile(
    data:         UpdateProfileRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Смена username.
    Создаёт новую версию пользователя.
    """
    # Проверяем что username не занят
    existing = (
        db.query(User)
        .filter_by(username=data.username, is_current=True)
        .first()
    )
    if existing and existing.entity_id != current_user.entity_id:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail      = "Username уже занят",
        )

    if data.username == current_user.username:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Новый username совпадает с текущим",
        )

    updated = create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = current_user.entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "username_change",
        username      = data.username,
    )
    return updated


@router.patch("/me/email", response_model=UserPublic)
def update_email(
    data:         UpdateEmailRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Смена email.
    Требует подтверждение текущего пароля.
    Создаёт новую версию пользователя.
    """
    # Проверяем пароль
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Неверный пароль",
        )

    # Email не должен меняться на тот же
    if data.new_email == current_user.email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Новый email совпадает с текущим",
        )

    # Email должен быть свободен
    if get_user_by_email(db, data.new_email):
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail      = "Email уже используется",
        )

    updated = create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = current_user.entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "email_change",
        email         = data.new_email,
    )
    return updated


@router.patch("/me/location", response_model=UserPublic)
def update_location(
    country:      str | None = None,
    city:         str | None = None,
    district:     str | None = None,
    db:           Session    = Depends(get_db),
    current_user: User       = Depends(get_current_user),
):
    """Обновить геолокацию пользователя."""
    if not any([country, city, district]):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Укажи хотя бы одно поле",
        )

    fields = {}
    if country:
        fields["country"]  = country
    if city:
        fields["city"]     = city
    if district:
        fields["district"] = district

    return create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = current_user.entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "location_update",
        **fields,
    )


@router.patch("/me/deactivate", response_model=UserPublic)
def deactivate_me(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Деактивация аккаунта — мягкая метка."""
    if current_user.status == UserStatus.deactivated:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail      = "Аккаунт уже деактивирован",
        )
    return create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = current_user.entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "self_deactivation",
        status        = UserStatus.deactivated,
    )


@router.get("/me/problems", response_model=ProblemList)
def get_my_problems(
    status:       ProblemStatus | None = Query(None),
    offset:       int                  = Query(0,  ge=0),
    limit:        int                  = Query(20, ge=1, le=100),
    db:           Session              = Depends(get_db),
    current_user: User                 = Depends(get_current_user),
):
    """
    Мои проблемы — только текущие версии.
    Фильтр по статусу опциональный.
    """
    query = (
        db.query(Problem)
        .filter_by(
            author_entity_id = current_user.entity_id,
            is_current       = True,
        )
    )
    if status:
        query = query.filter(Problem.status == status)

    total    = query.count()
    problems = (
        query
        .order_by(Problem.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.get("/me/votes", response_model=list[VotePublic])
def get_my_votes(
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Мои текущие голоса.
    Показывает последнюю версию каждого голоса.
    """
    return (
        db.query(Vote)
        .filter_by(
            user_entity_id = current_user.entity_id,
            is_current     = True,
        )
        .order_by(Vote.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/me/comments", response_model=list[CommentPublic])
def get_my_comments(
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Мои текущие комментарии."""
    return (
        db.query(Comment)
        .filter_by(
            author_entity_id = current_user.entity_id,
            is_current       = True,
        )
        .order_by(Comment.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/me/reputation", response_model=ReputationHistory)
def get_my_reputation(
    offset:       int     = Query(0,  ge=0),
    limit:        int     = Query(50, ge=1, le=200),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    История изменений моей репутации.
    Показывает все начисления и списания с причинами.
    """
    logs = (
        db.query(ReputationLog)
        .filter_by(user_entity_id=current_user.entity_id)
        .order_by(ReputationLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ReputationHistory(
        current_reputation = current_user.reputation,
        logs               = logs,
    )


# ── Публичные профили ─────────────────────────────────────

@router.get("/{entity_id}", response_model=UserPublic)
def get_user(entity_id: int, db: Session = Depends(get_db)):
    """Публичный профиль пользователя."""
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.get("/{entity_id}/problems", response_model=ProblemList)
def get_user_problems(
    entity_id:    int,
    status:       ProblemStatus | None = Query(None),
    offset:       int                  = Query(0,  ge=0),
    limit:        int                  = Query(20, ge=1, le=100),
    db:           Session              = Depends(get_db),
):
    """
    Публичные проблемы пользователя.
    Доступно без авторизации.
    """
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    query = (
        db.query(Problem)
        .filter_by(
            author_entity_id = entity_id,
            is_current       = True,
        )
    )
    if status:
        query = query.filter(Problem.status == status)

    total    = query.count()
    problems = (
        query
        .order_by(Problem.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )