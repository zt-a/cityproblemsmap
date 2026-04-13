# app/workers/tasks_notifications.py
from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app.models.user import User
from app.models.user_settings import UserNotificationSettings
from app.models.subscription import Subscription
from app.models.problem import Problem
from app.models.activity import Activity
from app.services.email import send_email
from app.config import settings


@shared_task(name="send_weekly_digest")
def send_weekly_digest():
    """Отправить еженедельный дайджест подписчикам"""
    db = SessionLocal()
    try:
        # Получить пользователей с включённым еженедельным дайджестом
        today = datetime.now(timezone.utc).weekday()  # 0 = Monday, 6 = Sunday

        user_settings = (
            db.query(UserNotificationSettings)
            .filter(
                UserNotificationSettings.is_current == True,
                UserNotificationSettings.digest_enabled == True,
                UserNotificationSettings.digest_frequency == "weekly",
                or_(
                    UserNotificationSettings.digest_day == today,
                    UserNotificationSettings.digest_day == None,  # По умолчанию понедельник
                ),
            )
            .all()
        )

        for user_setting in user_settings:
            user = (
                db.query(User)
                .filter_by(entity_id=user_setting.user_entity_id, is_current=True)
                .first()
            )

            if not user:
                continue

            # Собрать статистику за неделю
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)

            # Подписки пользователя
            subscriptions = (
                db.query(Subscription)
                .filter_by(user_entity_id=user.entity_id, is_current=True)
                .all()
            )

            if not subscriptions:
                continue

            # Собрать проблемы по подпискам
            problem_ids = [
                s.target_entity_id
                for s in subscriptions
                if s.target_type == "problem"
            ]

            # Активность по подписанным проблемам
            activities = (
                db.query(Activity)
                .filter(
                    Activity.target_type == "problem",
                    Activity.target_entity_id.in_(problem_ids),
                    Activity.created_at >= week_ago,
                )
                .order_by(Activity.created_at.desc())
                .limit(20)
                .all()
            )

            # Новые проблемы в подписанных зонах
            zone_ids = [s.target_entity_id for s in subscriptions if s.target_type == "zone"]

            new_problems = []
            if zone_ids:
                new_problems = (
                    db.query(Problem)
                    .filter(
                        Problem.zone_entity_id.in_(zone_ids),
                        Problem.created_at >= week_ago,
                        Problem.is_current == True,
                    )
                    .order_by(Problem.created_at.desc())
                    .limit(10)
                    .all()
                )

            # Отправить дайджест
            if activities or new_problems:
                _send_digest_email(db, user, activities, new_problems, "weekly")

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task(name="send_daily_digest")
def send_daily_digest():
    """Отправить ежедневный дайджест"""
    db = SessionLocal()
    try:
        user_settings = (
            db.query(UserNotificationSettings)
            .filter(
                UserNotificationSettings.is_current == True,
                UserNotificationSettings.digest_enabled == True,
                UserNotificationSettings.digest_frequency == "daily",
            )
            .all()
        )

        for user_setting in user_settings:
            user = (
                db.query(User)
                .filter_by(entity_id=user_setting.user_entity_id, is_current=True)
                .first()
            )

            if not user:
                continue

            day_ago = datetime.now(timezone.utc) - timedelta(days=1)

            subscriptions = (
                db.query(Subscription)
                .filter_by(user_entity_id=user.entity_id, is_current=True)
                .all()
            )

            if not subscriptions:
                continue

            problem_ids = [
                s.target_entity_id
                for s in subscriptions
                if s.target_type == "problem"
            ]

            activities = (
                db.query(Activity)
                .filter(
                    Activity.target_type == "problem",
                    Activity.target_entity_id.in_(problem_ids),
                    Activity.created_at >= day_ago,
                )
                .order_by(Activity.created_at.desc())
                .limit(10)
                .all()
            )

            zone_ids = [s.target_entity_id for s in subscriptions if s.target_type == "zone"]

            new_problems = []
            if zone_ids:
                new_problems = (
                    db.query(Problem)
                    .filter(
                        Problem.zone_entity_id.in_(zone_ids),
                        Problem.created_at >= day_ago,
                        Problem.is_current == True,
                    )
                    .order_by(Problem.created_at.desc())
                    .limit(5)
                    .all()
                )

            if activities or new_problems:
                _send_digest_email(db, user, activities, new_problems, "daily")

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def _send_digest_email(
    db: Session,
    user: User,
    activities: list[Activity],
    new_problems: list[Problem],
    frequency: str,
):
    """Отправить email с дайджестом"""
    frequency_text = {
        "daily": "Ежедневный",
        "weekly": "Еженедельный",
        "monthly": "Ежемесячный",
    }

    activities_html = ""
    if activities:
        activities_html = "<h3>Активность по вашим подпискам:</h3><ul>"
        for activity in activities[:10]:
            activities_html += f"<li>{activity.description or activity.action_type}</li>"
        activities_html += "</ul>"

    problems_html = ""
    if new_problems:
        problems_html = "<h3>Новые проблемы в ваших районах:</h3><ul>"
        for problem in new_problems[:10]:
            problem_url = f"{settings.FRONTEND_URL}/problems/{problem.entity_id}"
            problems_html += f'<li><a href="{problem_url}">{problem.title}</a> - {problem.status}</li>'
        problems_html += "</ul>"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1E3A5F;">{frequency_text[frequency]} дайджест — City Problems Map</h2>
        <p>Привет, <strong>{user.username}</strong>!</p>
        <p>Вот что произошло за последнее время:</p>
        {activities_html}
        {problems_html}
        <a href="{settings.FRONTEND_URL}/dashboard"
           style="
               display: inline-block;
               padding: 12px 24px;
               background-color: #2E75B6;
               color: white;
               text-decoration: none;
               border-radius: 6px;
               margin: 16px 0;
           ">
            Перейти на платформу
        </a>
        <hr style="border: 1px solid #eee; margin: 24px 0;">
        <p style="color: #999; font-size: 12px;">
            Вы получили это письмо, потому что подписаны на дайджест.<br>
            <a href="{settings.FRONTEND_URL}/settings/notifications">Изменить настройки</a>
        </p>
    </body>
    </html>
    """

    send_email(
        to=user.email,
        subject=f"{frequency_text[frequency]} дайджест — City Problems Map",
        html_body=html,
    )


@shared_task(name="send_notification_email")
def send_notification_email(
    user_email: str,
    subject: str,
    html_body: str,
):
    """Асинхронная отправка email уведомления"""
    try:
        send_email(to=user_email, subject=subject, html_body=html_body)
    except Exception as e:
        # Логирование ошибки
        print(f"Failed to send email to {user_email}: {e}")
        raise
