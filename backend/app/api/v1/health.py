# app/api/v1/health.py
from fastapi import APIRouter, status
from sqlalchemy import text
from app.database import engine
from app.services.redis_client import redis_client
from app.workers.celery_app import celery_app
from datetime import datetime, timezone

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check():
    """Базовая проверка работоспособности API"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/detailed")
def detailed_health_check():
    """
    Детальная проверка всех компонентов системы.
    Проверяет: PostgreSQL, Redis, Celery
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {}
    }

    # Проверка PostgreSQL
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        health_status["services"]["database"] = {
            "status": "healthy",
            "type": "postgresql"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Проверка Redis
    try:
        redis_client.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "type": "redis"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Проверка Celery
    try:

        # Проверяем активные воркеры
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()

        if active_workers:
            health_status["services"]["celery"] = {
                "status": "healthy",
                "workers": list(active_workers.keys()),
                "worker_count": len(active_workers)
            }
        else:
            health_status["status"] = "degraded"
            health_status["services"]["celery"] = {
                "status": "unhealthy",
                "error": "No active workers found"
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["celery"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Устанавливаем HTTP статус код
    http_status = status.HTTP_200_OK
    if health_status["status"] == "degraded":
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE  # noqa: F841

    return health_status


@router.get("/ready")
def readiness_check():
    """
    Проверка готовности к приёму запросов (для Kubernetes).
    Проверяет только критичные сервисы: БД и Redis.
    """
    try:
        # Проверка БД
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Проверка Redis
        redis_client.ping()

        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/live")
def liveness_check():
    """
    Проверка живости приложения (для Kubernetes).
    Простая проверка что процесс работает.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
