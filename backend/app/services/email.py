# app/services/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import Dict, Any
from app.config import settings

# Настройка Jinja2 для email templates
template_dir = Path(__file__).parent.parent / "templates" / "email"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))


def send_email(to: str, subject: str, html_body: str) -> None:
    """
    Отправляет email через Gmail SMTP.
    Использует STARTTLS на порту 587.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM, to, msg.as_string())


def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """Рендерит email template с контекстом"""
    template = jinja_env.get_template(template_name)
    return template.render(**context)


def send_reset_password_email(to: str, reset_token: str, username: str) -> None:
    """
    Отправляет письмо со ссылкой для сброса пароля.
    Ссылка ведёт на фронтенд — он потом вызывает /auth/reset-password.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1E3A5F;">Сброс пароля — City Problems Map</h2>
        <p>Привет, <strong>{username}</strong>!</p>
        <p>Ты запросил сброс пароля. Нажми на кнопку ниже:</p>
        <a href="{reset_url}"
           style="
               display: inline-block;
               padding: 12px 24px;
               background-color: #2E75B6;
               color: white;
               text-decoration: none;
               border-radius: 6px;
               margin: 16px 0;
           ">
            Сбросить пароль
        </a>
        <p style="color: #666; font-size: 14px;">
            Ссылка действует <strong>{settings.RESET_PASSWORD_EXPIRE_MINUTES} минут</strong>.
        </p>
        <p style="color: #666; font-size: 14px;">
            Если ты не запрашивал сброс — просто игнорируй это письмо.
        </p>
        <hr style="border: 1px solid #eee; margin: 24px 0;">
        <p style="color: #999; font-size: 12px;">
            City Problems Map — Digital Twin города
        </p>
    </body>
    </html>
    """

    send_email(
        to       = to,
        subject  = "Сброс пароля — City Problems Map",
        html_body = html,
    )


def send_welcome_email(to: str, username: str) -> None:
    """Отправляет приветственное письмо новому пользователю"""
    html = render_email_template("welcome.html", {
        "title": "Добро пожаловать!",
        "user_name": username,
        "frontend_url": settings.FRONTEND_URL,
        "support_email": settings.SMTP_FROM,
    })
    send_email(to, "Добро пожаловать в CityProblemMap!", html)


def send_new_comment_email(to: str, user_name: str, commenter_name: str,
                          problem_title: str, comment_text: str, problem_id: int) -> None:
    """Уведомление о новом комментарии"""
    problem_url = f"{settings.FRONTEND_URL}/problems/{problem_id}"
    html = render_email_template("new_comment.html", {
        "title": "Новый комментарий",
        "user_name": user_name,
        "commenter_name": commenter_name,
        "problem_title": problem_title,
        "comment_text": comment_text,
        "problem_url": problem_url,
    })
    send_email(to, f"Новый комментарий к проблеме: {problem_title}", html)


def send_status_changed_email(to: str, user_name: str, problem_title: str,
                              old_status: str, new_status: str, problem_id: int,
                              comment: str = None) -> None:
    """Уведомление об изменении статуса проблемы"""
    problem_url = f"{settings.FRONTEND_URL}/problems/{problem_id}"
    html = render_email_template("status_changed.html", {
        "title": "Изменение статуса проблемы",
        "user_name": user_name,
        "problem_title": problem_title,
        "old_status": old_status,
        "new_status": new_status,
        "comment": comment,
        "problem_url": problem_url,
    })
    send_email(to, f"Статус проблемы изменён: {problem_title}", html)


def send_new_problem_nearby_email(to: str, user_name: str, district: str,
                                  problem_title: str, problem_type: str,
                                  problem_description: str, problem_address: str,
                                  problem_id: int) -> None:
    """Уведомление о новой проблеме в районе пользователя"""
    problem_url = f"{settings.FRONTEND_URL}/problems/{problem_id}"
    html = render_email_template("new_problem_nearby.html", {
        "title": "Новая проблема в вашем районе",
        "user_name": user_name,
        "district": district,
        "problem_title": problem_title,
        "problem_type": problem_type,
        "problem_description": problem_description,
        "problem_address": problem_address,
        "problem_url": problem_url,
    })
    send_email(to, f"Новая проблема в районе {district}", html)


def send_achievement_email(to: str, user_name: str, achievement_name: str,
                          achievement_description: str, achievement_icon: str,
                          points: int, user_level: str, total_points: int) -> None:
    """Уведомление о получении достижения"""
    profile_url = f"{settings.FRONTEND_URL}/profile"
    html = render_email_template("achievement_unlocked.html", {
        "title": "Новое достижение!",
        "user_name": user_name,
        "achievement_name": achievement_name,
        "achievement_description": achievement_description,
        "achievement_icon": achievement_icon,
        "points": points,
        "user_level": user_level,
        "total_points": total_points,
        "profile_url": profile_url,
    })
    send_email(to, f"Новое достижение: {achievement_name}!", html)