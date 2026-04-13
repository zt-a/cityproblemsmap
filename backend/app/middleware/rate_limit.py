# app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.services.redis_client import redis_client


def get_user_identifier(request: Request) -> str:
    """
    Получить идентификатор пользователя для rate limiting.
    Использует user_id если авторизован, иначе IP адрес.
    """
    # Проверяем авторизацию
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.entity_id}"

    # Fallback на IP адрес
    return get_remote_address(request)


# Создаем limiter с Redis storage
limiter = Limiter(
    key_func=get_user_identifier,
    storage_uri=None,  # Будет установлен в main.py через redis_client
    default_limits=["1000/hour"],  # Дефолтный лимит для всех endpoints
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Кастомный обработчик ошибки превышения лимита"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Слишком много запросов. Попробуйте позже.",
            "error": "rate_limit_exceeded",
        },
    )
