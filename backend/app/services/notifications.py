# app/services/notifications.py
import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.redis_client import redis_client

logger = logging.getLogger(__name__)


def send_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    related_entity_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    action_url: Optional[str] = None,
):
    """
    Отправить уведомление пользователю.

    1. Сохраняет в БД (для истории)
    2. Отправляет через WebSocket (Redis pub/sub)

    Args:
        db: Database session
        user_id: ID пользователя
        notification_type: Тип уведомления (new_comment, status_changed, etc.)
        title: Заголовок уведомления
        message: Текст уведомления
        related_entity_id: ID связанной сущности (problem_id, comment_id, etc.)
        related_entity_type: Тип связанной сущности (problem, comment, etc.)
        action_url: URL для перехода при клике
    """
    try:
        # 1. Сохранить в БД
        entity_id = Notification.next_entity_id(db)
        notification = Notification(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
            action_url=action_url,
            is_read=False,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # 2. Отправить через WebSocket (Redis pub/sub)
        notification_data = {
            "type": notification_type,
            "notification_id": entity_id,
            "title": title,
            "message": message,
            "related_entity_id": related_entity_id,
            "related_entity_type": related_entity_type,
            "action_url": action_url,
            "created_at": notification.created_at.isoformat(),
        }

        redis_client.publish(
            f"notifications:{user_id}",
            json.dumps(notification_data)
        )

        logger.info(f"Notification sent to user {user_id}: {notification_type}")

    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")
        # Не падаем если уведомление не отправилось - это не критично


def broadcast_problem_update(
    problem_id: int,
    update_type: str,
    data: dict,
):
    """
    Отправить обновление проблемы всем подписчикам через WebSocket.

    Args:
        problem_id: ID проблемы
        update_type: Тип обновления (comment_added, vote_changed, etc.)
        data: Данные обновления
    """
    try:
        message = {
            "type": update_type,
            "problem_id": problem_id,
            "data": data,
        }

        redis_client.publish(
            f"problem:{problem_id}",
            json.dumps(message)
        )

        logger.debug(f"Problem {problem_id} update broadcasted: {update_type}")

    except Exception as e:
        logger.error(f"Error broadcasting problem update: {e}")
