# app/api/v1/moderation.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.moderation import BanUserRequest, UnbanUserRequest, BanInfo, BannedUsersList
from app.api.deps import require_role
from app.services.versioning import create_new_version

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.post("/users/{entity_id}/ban", response_model=BanInfo)
def ban_user(
    entity_id: int,
    data: BanUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Заблокировать пользователя.
    Доступно только модераторам и админам.

    duration_days:
    - None или 0 = постоянная блокировка
    - > 0 = временная блокировка на N дней
    """
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Нельзя забанить самого себя
    if user.entity_id == current_user.entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя забанить самого себя",
        )

    # Нельзя забанить админа (если ты не админ)
    if user.role == UserRole.admin and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только админ может забанить админа",
        )

    # Проверяем что пользователь не забанен
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже забанен",
        )

    # Вычисляем дату окончания бана
    ban_until = None
    if data.duration_days and data.duration_days > 0:
        ban_until = datetime.now(timezone.utc) + timedelta(days=data.duration_days)

    # Создаем новую версию с баном
    updated = create_new_version(
        db=db,
        model_class=User,
        entity_id=entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="banned_by_moderator",
        is_banned=True,
        ban_reason=data.reason,
        ban_until=ban_until,
        banned_by_entity_id=current_user.entity_id,
        banned_at=datetime.now(timezone.utc),
    )

    return BanInfo(
        is_banned=updated.is_banned,
        ban_reason=updated.ban_reason,
        ban_until=updated.ban_until,
        banned_by_entity_id=updated.banned_by_entity_id,
        banned_at=updated.banned_at,
    )


@router.post("/users/{entity_id}/unban", response_model=BanInfo)
def unban_user(
    entity_id: int,
    data: UnbanUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Разблокировать пользователя.
    Доступно только модераторам и админам.
    """
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не забанен",
        )

    # Разбаниваем
    updated = create_new_version(
        db=db,
        model_class=User,
        entity_id=entity_id,
        changed_by_id=current_user.entity_id,
        change_reason=f"unbanned: {data.reason}",
        is_banned=False,
        ban_reason=None,
        ban_until=None,
        banned_by_entity_id=None,
        banned_at=None,
    )

    return BanInfo(
        is_banned=updated.is_banned,
        ban_reason=updated.ban_reason,
        ban_until=updated.ban_until,
        banned_by_entity_id=updated.banned_by_entity_id,
        banned_at=updated.banned_at,
    )


@router.get("/users/{entity_id}/ban-info", response_model=BanInfo)
def get_ban_info(
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Получить информацию о бане пользователя.
    Доступно только модераторам и админам.
    """
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return BanInfo(
        is_banned=user.is_banned,
        ban_reason=user.ban_reason,
        ban_until=user.ban_until,
        banned_by_entity_id=user.banned_by_entity_id,
        banned_at=user.banned_at,
    )


@router.get("/banned-users", response_model=BannedUsersList)
def get_banned_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    """
    Получить список забаненных пользователей.
    Доступно только модераторам и админам.
    """
    query = db.query(User).filter_by(is_current=True, is_banned=True)

    total = query.count()
    users = (
        query
        .order_by(User.banned_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = [
        {
            "entity_id": user.entity_id,
            "username": user.username,
            "email": user.email,
            "is_banned": user.is_banned,
            "ban_reason": user.ban_reason,
            "ban_until": user.ban_until.isoformat() if user.ban_until else None,
            "banned_by_entity_id": user.banned_by_entity_id,
            "banned_at": user.banned_at.isoformat() if user.banned_at else None,
        }
        for user in users
    ]

    return BannedUsersList(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/check-expired-bans")
def check_expired_bans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    """
    Проверить и разбанить пользователей с истекшим сроком бана.
    Доступно только админам.
    Можно запускать по расписанию через Celery.
    """
    now = datetime.now(timezone.utc)

    # Находим пользователей с истекшим баном
    expired_bans = (
        db.query(User)
        .filter(
            User.is_current,
            User.is_banned,
            User.ban_until is not None,
            User.ban_until <= now,
        )
        .all()
    )

    unbanned_count = 0
    for user in expired_bans:
        create_new_version(
            db=db,
            model_class=User,
            entity_id=user.entity_id,
            changed_by_id=0,  # Система
            change_reason="ban_expired_automatically",
            is_banned=False,
            ban_reason=None,
            ban_until=None,
            banned_by_entity_id=None,
            banned_at=None,
        )
        unbanned_count += 1

    return {
        "message": f"Разбанено {unbanned_count} пользователей",
        "unbanned_count": unbanned_count,
    }
