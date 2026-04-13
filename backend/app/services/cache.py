# app/services/cache.py
import json
import hashlib
from typing import Any, Callable, Optional
from functools import wraps
from app.services.redis_client import redis_client


class CacheService:
    """Сервис для кеширования данных в Redis"""

    DEFAULT_TTL = 300  # 5 минут по умолчанию

    @staticmethod
    def _make_key(prefix: str, *args, **kwargs) -> str:
        """Генерирует уникальный ключ кеша на основе аргументов"""
        key_parts = [prefix]

        # Добавляем позиционные аргументы
        for arg in args:
            if isinstance(arg, (int, str, float, bool)):
                key_parts.append(str(arg))

        # Добавляем именованные аргументы (сортируем для стабильности)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (int, str, float, bool)):
                key_parts.append(f"{k}={v}")

        key = ":".join(key_parts)

        # Если ключ слишком длинный, используем хеш
        if len(key) > 200:
            hash_suffix = hashlib.md5(key.encode()).hexdigest()[:8]
            key = f"{prefix}:hash:{hash_suffix}"

        return key

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """Сохранить значение в кеш"""
        try:
            serialized = json.dumps(value, default=str)
            redis_client.setex(key, ttl, serialized)
            return True
        except Exception:
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Удалить значение из кеша"""
        try:
            redis_client.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Удалить все ключи по паттерну"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

    @staticmethod
    def exists(key: str) -> bool:
        """Проверить существование ключа"""
        try:
            return redis_client.exists(key) > 0
        except Exception:
            return False


def cached(prefix: str, ttl: int = CacheService.DEFAULT_TTL):
    """
    Декоратор для кеширования результатов функций

    Usage:
        @cached("problems:popular", ttl=600)
        def get_popular_problems(city: str, limit: int = 10):
            # ...
            return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кеша
            cache_key = CacheService._make_key(prefix, *args, **kwargs)

            # Пытаемся получить из кеша
            cached_value = CacheService.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Вызываем функцию
            result = func(*args, **kwargs)

            # Сохраняем в кеш
            CacheService.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# ── Специфичные функции кеширования ──────────────────────────

def cache_problem(problem_id: int, data: dict, ttl: int = 300) -> bool:
    """Кешировать данные проблемы"""
    key = f"problem:{problem_id}"
    return CacheService.set(key, data, ttl)


def get_cached_problem(problem_id: int) -> Optional[dict]:
    """Получить проблему из кеша"""
    key = f"problem:{problem_id}"
    return CacheService.get(key)


def invalidate_problem_cache(problem_id: int) -> bool:
    """Инвалидировать кеш проблемы"""
    key = f"problem:{problem_id}"
    return CacheService.delete(key)


def cache_zone_stats(zone_id: int, stats: dict, ttl: int = 600) -> bool:
    """Кешировать статистику зоны"""
    key = f"zone:stats:{zone_id}"
    return CacheService.set(key, stats, ttl)


def get_cached_zone_stats(zone_id: int) -> Optional[dict]:
    """Получить статистику зоны из кеша"""
    key = f"zone:stats:{zone_id}"
    return CacheService.get(key)


def invalidate_zone_cache(zone_id: int) -> bool:
    """Инвалидировать кеш зоны"""
    pattern = f"zone:*:{zone_id}"
    return CacheService.delete_pattern(pattern) > 0


def cache_user_profile(user_id: int, profile: dict, ttl: int = 600) -> bool:
    """Кешировать профиль пользователя"""
    key = f"user:profile:{user_id}"
    return CacheService.set(key, profile, ttl)


def get_cached_user_profile(user_id: int) -> Optional[dict]:
    """Получить профиль пользователя из кеша"""
    key = f"user:profile:{user_id}"
    return CacheService.get(key)


def invalidate_user_cache(user_id: int) -> bool:
    """Инвалидировать кеш пользователя"""
    pattern = f"user:*:{user_id}"
    return CacheService.delete_pattern(pattern) > 0


def cache_popular_problems(city: str, problems: list, ttl: int = 300) -> bool:
    """Кешировать популярные проблемы города"""
    key = f"problems:popular:{city}"
    return CacheService.set(key, problems, ttl)


def get_cached_popular_problems(city: str) -> Optional[list]:
    """Получить популярные проблемы из кеша"""
    key = f"problems:popular:{city}"
    return CacheService.get(key)


def invalidate_popular_problems_cache(city: str) -> bool:
    """Инвалидировать кеш популярных проблем"""
    key = f"problems:popular:{city}"
    return CacheService.delete(key)


def cache_analytics(metric: str, period: str, filters: dict, data: Any, ttl: int = 600) -> bool:
    """Кешировать аналитические данные"""
    key = CacheService._make_key(f"analytics:{metric}:{period}", **filters)
    return CacheService.set(key, data, ttl)


def get_cached_analytics(metric: str, period: str, filters: dict) -> Optional[Any]:
    """Получить аналитику из кеша"""
    key = CacheService._make_key(f"analytics:{metric}:{period}", **filters)
    return CacheService.get(key)


def invalidate_analytics_cache(metric: Optional[str] = None) -> int:
    """Инвалидировать кеш аналитики"""
    pattern = f"analytics:{metric}:*" if metric else "analytics:*"
    return CacheService.delete_pattern(pattern)


def cache_leaderboard(leaderboard_type: str, data: list, ttl: int = 600) -> bool:
    """Кешировать таблицу лидеров"""
    key = f"leaderboard:{leaderboard_type}"
    return CacheService.set(key, data, ttl)


def get_cached_leaderboard(leaderboard_type: str) -> Optional[list]:
    """Получить таблицу лидеров из кеша"""
    key = f"leaderboard:{leaderboard_type}"
    return CacheService.get(key)


def invalidate_leaderboard_cache() -> int:
    """Инвалидировать весь кеш таблиц лидеров"""
    return CacheService.delete_pattern("leaderboard:*")
