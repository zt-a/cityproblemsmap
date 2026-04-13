# app/services/captcha.py
import requests
from typing import Optional
from app.config import settings


def verify_recaptcha(token: str, remote_ip: Optional[str] = None) -> bool:
    """
    Проверить Google reCAPTCHA v3 token.

    Args:
        token: Token от клиента
        remote_ip: IP адрес клиента (опционально)

    Returns:
        True если CAPTCHA валидна, False иначе

    Usage:
        if not verify_recaptcha(captcha_token, request.client.host):
            raise HTTPException(400, "Invalid CAPTCHA")
    """
    # Если CAPTCHA отключена в настройках (для разработки)
    if not settings.RECAPTCHA_SECRET_KEY:
        return True

    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": token,
                "remoteip": remote_ip
            },
            timeout=5
        )

        result = response.json()

        # reCAPTCHA v3 возвращает score от 0.0 до 1.0
        # 1.0 - точно человек, 0.0 - точно бот
        # Рекомендуемый порог: 0.5
        if result.get("success") and result.get("score", 0) >= 0.5:
            return True

        return False

    except Exception:
        # Если сервис недоступен, пропускаем (не блокируем пользователей)
        return True


def verify_hcaptcha(token: str, remote_ip: Optional[str] = None) -> bool:
    """
    Проверить hCaptcha token.

    Args:
        token: Token от клиента
        remote_ip: IP адрес клиента (опционально)

    Returns:
        True если CAPTCHA валидна, False иначе
    """
    # Если CAPTCHA отключена в настройках
    if not settings.HCAPTCHA_SECRET_KEY:
        return True

    try:
        response = requests.post(
            "https://hcaptcha.com/siteverify",
            data={
                "secret": settings.HCAPTCHA_SECRET_KEY,
                "response": token,
                "remoteip": remote_ip
            },
            timeout=5
        )

        result = response.json()
        return result.get("success", False)

    except Exception:
        # Если сервис недоступен, пропускаем
        return True


def verify_turnstile(token: str, remote_ip: Optional[str] = None) -> bool:
    """
    Проверить Cloudflare Turnstile token.

    Args:
        token: Token от клиента
        remote_ip: IP адрес клиента (опционально)

    Returns:
        True если CAPTCHA валидна, False иначе
    """
    # Если CAPTCHA отключена в настройках
    if not settings.TURNSTILE_SECRET_KEY:
        return True

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            json={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": remote_ip
            },
            timeout=5
        )

        result = response.json()
        return result.get("success", False)

    except Exception:
        # Если сервис недоступен, пропускаем
        return True


# Алиас для основной функции (по умолчанию используем reCAPTCHA)
verify_captcha = verify_recaptcha
