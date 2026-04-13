# app/services/email_notifications.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.problem import Problem
from app.models.comment import Comment
from app.models.user_settings import UserNotificationSettings
from app.services.email import send_email
from app.config import settings
from typing import Optional
from datetime import datetime, timezone


class EmailNotificationService:
    """Сервис для отправки email уведомлений"""

    @staticmethod
    def _should_send_email(db: Session, user_id: int, notification_type: str) -> bool:
        """Проверяет, нужно ли отправлять email уведомление"""
        user_settings = (
            db.query(UserNotificationSettings)
            .filter_by(user_entity_id=user_id, is_current=True)
            .first()
        )

        if not user_settings or not user_settings.email_enabled:
            return False

        # Проверка тихих часов
        if user_settings.quiet_hours_enabled:
            current_hour = datetime.now(timezone.utc).hour
            start = user_settings.quiet_hours_start or 0
            end = user_settings.quiet_hours_end or 0

            if start < end:
                if start <= current_hour < end:
                    return False
            else:  # Переход через полночь
                if current_hour >= start or current_hour < end:
                    return False

        # Проверка конкретного типа уведомления
        type_mapping = {
            "comment": user_settings.email_on_comment,
            "status_change": user_settings.email_on_status_change,
            "official_response": user_settings.email_on_official_response,
            "problem_solved": user_settings.email_on_problem_solved,
            "mention": user_settings.email_on_mention,
        }

        return type_mapping.get(notification_type, True)

    @staticmethod
    def send_problem_comment_email(
        db: Session,
        user: User,
        problem: Problem,
        comment: Comment,
        commenter_username: str,
    ):
        """Отправить email о новом комментарии"""
        if not EmailNotificationService._should_send_email(db, user.entity_id, "comment"):
            return

        problem_url = f"{settings.FRONTEND_URL}/problems/{problem.entity_id}"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1E3A5F;">Новый комментарий к вашей проблеме</h2>
            <p>Привет, <strong>{user.username}</strong>!</p>
            <p>Пользователь <strong>{commenter_username}</strong> оставил комментарий к проблеме:</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2E75B6; margin: 20px 0;">
                <h3 style="margin-top: 0;">{problem.title}</h3>
                <p style="color: #666;">{comment.content[:200]}{"..." if len(comment.content) > 200 else ""}</p>
            </div>
            <a href="{problem_url}"
               style="
                   display: inline-block;
                   padding: 12px 24px;
                   background-color: #2E75B6;
                   color: white;
                   text-decoration: none;
                   border-radius: 6px;
                   margin: 16px 0;
               ">
                Посмотреть проблему
            </a>
            <hr style="border: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                City Problems Map — Digital Twin города
            </p>
        </body>
        </html>
        """

        send_email(
            to=user.email,
            subject=f"Новый комментарий к проблеме: {problem.title}",
            html_body=html,
        )

    @staticmethod
    def send_status_change_email(
        db: Session,
        user: User,
        problem: Problem,
        old_status: str,
        new_status: str,
    ):
        """Отправить email об изменении статуса"""
        if not EmailNotificationService._should_send_email(db, user.entity_id, "status_change"):
            return

        problem_url = f"{settings.FRONTEND_URL}/problems/{problem.entity_id}"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1E3A5F;">Статус проблемы изменён</h2>
            <p>Привет, <strong>{user.username}</strong>!</p>
            <p>Статус вашей проблемы изменился:</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2E75B6; margin: 20px 0;">
                <h3 style="margin-top: 0;">{problem.title}</h3>
                <p><strong>Старый статус:</strong> {old_status}</p>
                <p><strong>Новый статус:</strong> <span style="color: #2E75B6;">{new_status}</span></p>
            </div>
            <a href="{problem_url}"
               style="
                   display: inline-block;
                   padding: 12px 24px;
                   background-color: #2E75B6;
                   color: white;
                   text-decoration: none;
                   border-radius: 6px;
                   margin: 16px 0;
               ">
                Посмотреть проблему
            </a>
            <hr style="border: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                City Problems Map — Digital Twin города
            </p>
        </body>
        </html>
        """

        send_email(
            to=user.email,
            subject=f"Статус проблемы изменён: {problem.title}",
            html_body=html,
        )

    @staticmethod
    def send_problem_solved_email(
        db: Session,
        user: User,
        problem: Problem,
    ):
        """Отправить email о решении проблемы"""
        if not EmailNotificationService._should_send_email(db, user.entity_id, "problem_solved"):
            return

        problem_url = f"{settings.FRONTEND_URL}/problems/{problem.entity_id}"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Проблема решена! 🎉</h2>
            <p>Привет, <strong>{user.username}</strong>!</p>
            <p>Отличные новости! Ваша проблема была решена:</p>
            <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #155724;">{problem.title}</h3>
                <p style="color: #155724;">Спасибо за вашу активную гражданскую позицию!</p>
            </div>
            <a href="{problem_url}"
               style="
                   display: inline-block;
                   padding: 12px 24px;
                   background-color: #28a745;
                   color: white;
                   text-decoration: none;
                   border-radius: 6px;
                   margin: 16px 0;
               ">
                Посмотреть проблему
            </a>
            <hr style="border: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                City Problems Map — Digital Twin города
            </p>
        </body>
        </html>
        """

        send_email(
            to=user.email,
            subject=f"Проблема решена: {problem.title}",
            html_body=html,
        )

    @staticmethod
    def send_official_response_email(
        db: Session,
        user: User,
        problem: Problem,
        response_text: str,
        official_username: str,
    ):
        """Отправить email об официальном ответе"""
        if not EmailNotificationService._should_send_email(db, user.entity_id, "official_response"):
            return

        problem_url = f"{settings.FRONTEND_URL}/problems/{problem.entity_id}"

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1E3A5F;">Официальный ответ на вашу проблему</h2>
            <p>Привет, <strong>{user.username}</strong>!</p>
            <p>Официальное лицо <strong>{official_username}</strong> ответило на вашу проблему:</p>
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <h3 style="margin-top: 0;">{problem.title}</h3>
                <p style="color: #856404;">{response_text[:300]}{"..." if len(response_text) > 300 else ""}</p>
            </div>
            <a href="{problem_url}"
               style="
                   display: inline-block;
                   padding: 12px 24px;
                   background-color: #ffc107;
                   color: #212529;
                   text-decoration: none;
                   border-radius: 6px;
                   margin: 16px 0;
               ">
                Посмотреть ответ
            </a>
            <hr style="border: 1px solid #eee; margin: 24px 0;">
            <p style="color: #999; font-size: 12px;">
                City Problems Map — Digital Twin города
            </p>
        </body>
        </html>
        """

        send_email(
            to=user.email,
            subject=f"Официальный ответ: {problem.title}",
            html_body=html,
        )
