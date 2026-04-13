# app/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для добавления заголовков безопасности.
    Защищает от XSS, clickjacking и других атак.
    """

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Content Security Policy - защита от XSS
        # response.headers["Content-Security-Policy"] = (
        #     "default-src 'self'; "
        #     "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        #     "style-src 'self' 'unsafe-inline'; "
        #     "img-src 'self' data: https:; "
        #     "font-src 'self' data:; "
        #     "connect-src 'self'; "
        #     "frame-ancestors 'none';"
        # )
        
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Защита от clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Предотвращение MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS Protection (для старых браузеров)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict Transport Security - принудительный HTTPS
        # Включать только в production с HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (ранее Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=()"
        )

        return response
