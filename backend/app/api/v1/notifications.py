# app/api/v1/notifications.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.schemas.notification import (
    NotificationPublic,
    NotificationList,
    MarkAsReadRequest,
    NotificationStats,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationList)
def get_notifications(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    notification_type: NotificationType | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить список уведомлений текущего пользователя"""
    query = db.query(Notification).filter(
        Notification.user_entity_id == current_user.entity_id,
        Notification.is_current
    )

    if unread_only:
        query = query.filter(not Notification.is_read)

    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)

    total = query.count()
    unread_count = (
        db.query(Notification)
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
            not Notification.is_read,
        )
        .count()
    )

    notifications = (
        query.order_by(desc(Notification.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return NotificationList(
        notifications=[NotificationPublic.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.get("/stats", response_model=NotificationStats)
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить статистику уведомлений"""
    total = (
        db.query(Notification)
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current
        )
        .count()
    )

    unread = (
        db.query(Notification)
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
            not Notification.is_read,
        )
        .count()
    )

    by_type_query = (
        db.query(
            Notification.notification_type,
            func.count(Notification.entity_id).label("count"),
        )
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current
        )
        .group_by(Notification.notification_type)
        .all()
    )

    by_type = {str(nt): count for nt, count in by_type_query}

    return NotificationStats(total=total, unread=unread, by_type=by_type)


@router.post("/mark-read")
def mark_notifications_as_read(
    data: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отметить уведомления как прочитанные (через версионирование)"""
    from app.services.versioning import create_new_version

    notifications = (
        db.query(Notification)
        .filter(
            Notification.entity_id.in_(data.notification_ids),
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
        )
        .all()
    )

    updated_count = 0
    for notification in notifications:
        if not notification.is_read:
            create_new_version(
                db=db,
                model_class=Notification,
                entity_id=notification.entity_id,
                changed_by_id=current_user.entity_id,
                change_reason="marked_as_read",
                is_read=True,
            )
            updated_count += 1

    db.commit()
    return {"message": f"Marked {updated_count} notifications as read"}


@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отметить все уведомления как прочитанные (через версионирование)"""
    from app.services.versioning import create_new_version

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
            not Notification.is_read,
        )
        .all()
    )

    for notification in notifications:
        create_new_version(
            db=db,
            model_class=Notification,
            entity_id=notification.entity_id,
            changed_by_id=current_user.entity_id,
            change_reason="marked_all_as_read",
            is_read=True,
        )

    db.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить уведомление (мягкое удаление через is_current)"""
    notification = (
        db.query(Notification)
        .filter(
            Notification.entity_id == notification_id,
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
        )
        .first()
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Мягкое удаление - помечаем как неактуальное
    notification.is_current = False
    notification.superseded_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Notification deleted"}


@router.delete("/")
def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить все уведомления пользователя (мягкое удаление)"""
    from datetime import datetime

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_entity_id == current_user.entity_id,
            Notification.is_current,
        )
        .all()
    )

    for notification in notifications:
        notification.is_current = False
        notification.superseded_at = datetime.now(timezone.utc)

    db.commit()
    return {"message": f"Deleted {len(notifications)} notifications"}
