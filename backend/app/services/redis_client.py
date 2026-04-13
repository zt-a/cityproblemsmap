# app/services/redis_client.py
import redis
from app.config import settings

# Один клиент на всё приложение
# Используем redis_url property который учитывает TESTING и LOCAL_DATABASE
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses = True,   # строки вместо bytes
)


# ── Blacklist для logout ──────────────────────────────────

def blacklist_token(token: str, expire_seconds: int) -> None:
    """
    Добавляет refresh токен в blacklist.
    Токен автоматически удаляется из Redis после истечения срока.
    """
    redis_client.setex(
        name  = f"blacklist:{token}",
        time  = expire_seconds,
        value = "1",
    )


def is_token_blacklisted(token: str) -> bool:
    """Проверяет находится ли токен в blacklist."""
    return redis_client.exists(f"blacklist:{token}") > 0


# ── Reset password токены ─────────────────────────────────

def save_reset_token(
    token:     str,
    entity_id: int,
    expire_seconds: int,
) -> None:
    """
    Сохраняет токен сброса пароля.
    Ключ: reset_password:{token} → entity_id пользователя
    """
    redis_client.setex(
        name  = f"reset_password:{token}",
        time  = expire_seconds,
        value = str(entity_id),
    )


def get_reset_token_entity_id(token: str) -> int | None:
    """
    Возвращает entity_id по токену сброса.
    None если токен не существует или истёк.
    """
    value = redis_client.get(f"reset_password:{token}")
    return int(value) if value else None


def delete_reset_token(token: str) -> None:
    """Удаляет токен после использования — одноразовый."""
    redis_client.delete(f"reset_password:{token}")