# app/api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.subscription import Subscription
from app.models.problem import Problem
from app.models.zone import Zone
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionPublic, SubscriptionList
from app.api.deps import get_current_user
from app.services.versioning import create_new_version

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _check_target_exists(db: Session, target_type: str, target_entity_id: int):
    """Проверяет существование цели подписки"""
    if target_type == "problem":
        target = db.query(Problem).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Проблема не найдена")
    elif target_type == "zone":
        target = db.query(Zone).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Зона не найдена")
    elif target_type == "user":
        target = db.query(User).filter_by(entity_id=target_entity_id, is_current=True).first()
        if not target:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    else:
        raise HTTPException(status_code=400, detail="Неверный тип цели")


@router.post("/problems/{problem_id}", response_model=SubscriptionPublic, status_code=201)
def subscribe_to_problem(
    problem_id: int,
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Подписаться на проблему"""
    _check_target_exists(db, "problem", problem_id)

    # Проверяем существующую подписку
    existing = (
        db.query(Subscription)
        .filter_by(
            user_entity_id=current_user.entity_id,
            target_type="problem",
            target_entity_id=problem_id,
            is_current=True,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Подписка уже существует",
        )

    entity_id = Subscription.next_entity_id(db)

    subscription = Subscription(
        entity_id=entity_id,
        version=1,
        is_current=True,
        user_entity_id=current_user.entity_id,
        target_type="problem",
        target_entity_id=problem_id,
        notification_types=data.notification_types,
        changed_by_id=current_user.entity_id,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/problems/{problem_id}", status_code=204)
def unsubscribe_from_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отписаться от проблемы"""
    subscription = (
        db.query(Subscription)
        .filter_by(
            user_entity_id=current_user.entity_id,
            target_type="problem",
            target_entity_id=problem_id,
            is_current=True,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    # Помечаем как неактуальную
    from datetime import datetime
    subscription.is_current = False
    subscription.superseded_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/zones/{zone_id}", response_model=SubscriptionPublic, status_code=201)
def subscribe_to_zone(
    zone_id: int,
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Подписаться на зону (район)"""
    _check_target_exists(db, "zone", zone_id)

    existing = (
        db.query(Subscription)
        .filter_by(
            user_entity_id=current_user.entity_id,
            target_type="zone",
            target_entity_id=zone_id,
            is_current=True,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Подписка уже существует",
        )

    entity_id = Subscription.next_entity_id(db)

    subscription = Subscription(
        entity_id=entity_id,
        version=1,
        is_current=True,
        user_entity_id=current_user.entity_id,
        target_type="zone",
        target_entity_id=zone_id,
        notification_types=data.notification_types,
        changed_by_id=current_user.entity_id,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/zones/{zone_id}", status_code=204)
def unsubscribe_from_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отписаться от зоны"""
    subscription = (
        db.query(Subscription)
        .filter_by(
            user_entity_id=current_user.entity_id,
            target_type="zone",
            target_entity_id=zone_id,
            is_current=True,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    from datetime import datetime
    subscription.is_current = False
    subscription.superseded_at = datetime.now(timezone.utc)
    db.commit()


@router.get("/", response_model=SubscriptionList)
def get_my_subscriptions(
    target_type: Optional[str] = Query(None, description="Фильтр по типу: problem/zone/user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить все подписки текущего пользователя"""
    query = db.query(Subscription).filter_by(
        user_entity_id=current_user.entity_id,
        is_current=True,
    )

    if target_type:
        query = query.filter_by(target_type=target_type)

    subscriptions = query.order_by(Subscription.created_at.desc()).all()

    return SubscriptionList(
        items=subscriptions,
        total=len(subscriptions),
    )


@router.patch("/{entity_id}", response_model=SubscriptionPublic)
def update_subscription(
    entity_id: int,
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить настройки подписки (типы уведомлений)"""
    subscription = (
        db.query(Subscription)
        .filter_by(
            entity_id=entity_id,
            user_entity_id=current_user.entity_id,
            is_current=True,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    updated = create_new_version(
        db=db,
        model_class=Subscription,
        entity_id=entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="notification_types_updated",
        notification_types=data.notification_types,
    )

    return updated
