# app/services/notification_service.py
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.problem import Problem
from app.models.comment import Comment
from typing import Optional


class NotificationService:
    """Сервис для создания и управления уведомлениями"""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        problem_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        actor_id: Optional[int] = None,
    ) -> Notification:
        """Создать уведомление"""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            problem_id=problem_id,
            comment_id=comment_id,
            actor_id=actor_id,
            is_read=False,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def notify_problem_status_changed(
        db: Session,
        problem: Problem,
        old_status: str,
        new_status: str,
        actor_id: Optional[int] = None,
    ):
        """Уведомить автора о изменении статуса проблемы"""
        NotificationService.create_notification(
            db=db,
            user_id=problem.author_entity_id,
            notification_type=NotificationType.PROBLEM_STATUS_CHANGED,
            title=f"Статус проблемы изменён: {new_status}",
            message=f'Статус вашей проблемы "{problem.title}" изменён с "{old_status}" на "{new_status}"',
            problem_id=problem.entity_id,
            actor_id=actor_id,
        )

    @staticmethod
    def notify_problem_assigned(
        db: Session,
        problem: Problem,
        official_id: int,
        actor_id: Optional[int] = None,
    ):
        """Уведомить официала о назначении проблемы"""
        NotificationService.create_notification(
            db=db,
            user_id=official_id,
            notification_type=NotificationType.PROBLEM_ASSIGNED,
            title="Вам назначена новая проблема",
            message=f'Проблема "{problem.title}" назначена вам для решения',
            problem_id=problem.entity_id,
            actor_id=actor_id,
        )

    @staticmethod
    def notify_problem_commented(
        db: Session,
        problem: Problem,
        comment: Comment,
        actor_id: int,
    ):
        """Уведомить автора проблемы о новом комментарии"""
        if problem.author_entity_id != actor_id:
            NotificationService.create_notification(
                db=db,
                user_id=problem.author_entity_id,
                notification_type=NotificationType.PROBLEM_COMMENTED,
                title="Новый комментарий к вашей проблеме",
                message=f'Пользователь оставил комментарий к проблеме "{problem.title}"',
                problem_id=problem.entity_id,
                comment_id=comment.entity_id,
                actor_id=actor_id,
            )

    @staticmethod
    def notify_comment_replied(
        db: Session,
        parent_comment: Comment,
        reply_comment: Comment,
        actor_id: int,
    ):
        """Уведомить автора комментария об ответе"""
        if parent_comment.author_entity_id != actor_id:
            NotificationService.create_notification(
                db=db,
                user_id=parent_comment.author_entity_id,
                notification_type=NotificationType.COMMENT_REPLIED,
                title="Ответ на ваш комментарий",
                message="Пользователь ответил на ваш комментарий",
                problem_id=parent_comment.problem_entity_id,
                comment_id=reply_comment.entity_id,
                actor_id=actor_id,
            )

    @staticmethod
    def notify_problem_upvoted(
        db: Session,
        problem: Problem,
        actor_id: int,
    ):
        """Уведомить автора о голосе за проблему (опционально, можно группировать)"""
        # Можно добавить логику группировки (например, уведомлять раз в день)
        pass

    @staticmethod
    def notify_problem_verified(
        db: Session,
        problem: Problem,
        actor_id: int,
    ):
        """Уведомить автора о подтверждении проблемы модератором"""
        NotificationService.create_notification(
            db=db,
            user_id=problem.author_entity_id,
            notification_type=NotificationType.PROBLEM_VERIFIED,
            title="Проблема подтверждена",
            message=f'Ваша проблема "{problem.title}" подтверждена модератором',
            problem_id=problem.entity_id,
            actor_id=actor_id,
        )

    @staticmethod
    def notify_problem_rejected(
        db: Session,
        problem: Problem,
        reason: str,
        actor_id: int,
    ):
        """Уведомить автора об отклонении проблемы"""
        NotificationService.create_notification(
            db=db,
            user_id=problem.author_entity_id,
            notification_type=NotificationType.PROBLEM_REJECTED,
            title="Проблема отклонена",
            message=f'Ваша проблема "{problem.title}" отклонена. Причина: {reason}',
            problem_id=problem.entity_id,
            actor_id=actor_id,
        )

    @staticmethod
    def notify_comment_hidden(
        db: Session,
        comment: Comment,
        reason: str,
        actor_id: int,
    ):
        """Уведомить автора о скрытии комментария"""
        NotificationService.create_notification(
            db=db,
            user_id=comment.author_entity_id,
            notification_type=NotificationType.COMMENT_HIDDEN,
            title="Комментарий скрыт",
            message=f"Ваш комментарий был скрыт модератором. Причина: {reason}",
            comment_id=comment.entity_id,
            actor_id=actor_id,
        )
