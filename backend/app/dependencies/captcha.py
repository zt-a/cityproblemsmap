# app/dependencies/captcha.py
from fastapi import Header, HTTPException, status
from typing import Optional
from app.services.captcha import verify_recaptcha, verify_hcaptcha, verify_turnstile
from app.config import settings


async def verify_captcha_token(
    x_captcha_token: Optional[str] = Header(None, description="CAPTCHA token"),
    x_captcha_type: Optional[str] = Header("recaptcha", description="CAPTCHA type: recaptcha, hcaptcha, turnstile")
) -> bool:
    """
    Dependency для проверки CAPTCHA токена.

    Использование:
    ```python
    @router.post("/endpoint")
    async def endpoint(captcha_verified: bool = Depends(verify_captcha_token)):
        ...
    ```
    """
    # Если CAPTCHA не настроена - пропускаем проверку (для dev)
    if not settings.RECAPTCHA_SECRET_KEY and not settings.HCAPTCHA_SECRET_KEY and not settings.TURNSTILE_SECRET_KEY:
        return True

    if not x_captcha_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CAPTCHA token is required"
        )

    # Выбираем провайдера CAPTCHA
    captcha_type = (x_captcha_type or "recaptcha").lower()

    try:
        if captcha_type == "recaptcha":
            if not settings.RECAPTCHA_SECRET_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="reCAPTCHA is not configured"
                )
            verified = verify_recaptcha(x_captcha_token)

        elif captcha_type == "hcaptcha":
            if not settings.HCAPTCHA_SECRET_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="hCaptcha is not configured"
                )
            verified = verify_hcaptcha(x_captcha_token)

        elif captcha_type == "turnstile":
            if not settings.TURNSTILE_SECRET_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cloudflare Turnstile is not configured"
                )
            verified = verify_turnstile(x_captcha_token)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown CAPTCHA type: {captcha_type}"
            )

        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CAPTCHA verification failed"
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CAPTCHA verification error: {str(e)}"
        )


async def verify_captcha_optional(
    x_captcha_token: Optional[str] = Header(None),
    x_captcha_type: Optional[str] = Header("recaptcha")
) -> bool:
    """
    Опциональная проверка CAPTCHA - не выбрасывает ошибку если токен не предоставлен.
    Используется для endpoints где CAPTCHA желательна но не обязательна.
    """
    if not x_captcha_token:
        return False

    try:
        return await verify_captcha_token(x_captcha_token, x_captcha_type)
    except HTTPException:
        return False
