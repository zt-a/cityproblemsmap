# tests/test_health.py
import pytest
from unittest.mock import patch, MagicMock


def test_health_check(client):
    """Базовая проверка работоспособности"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_liveness_check(client):
    """Проверка живости приложения"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


def test_readiness_check_success(client):
    """Проверка готовности - успешный случай"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "timestamp" in data


@patch("app.api.v1.health.engine.connect")
def test_readiness_check_db_failure(mock_connect, client):
    """Проверка готовности - БД недоступна"""
    mock_connect.side_effect = Exception("Database connection failed")

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_ready"
    assert "error" in data


def test_detailed_health_check_success(client):
    """Детальная проверка - все сервисы работают"""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

    # Проверяем наличие сервисов
    assert "database" in data["services"]
    assert "redis" in data["services"]
    assert "celery" in data["services"]


@patch("app.api.v1.health.engine.connect")
def test_detailed_health_check_db_failure(mock_connect, client):
    """Детальная проверка - БД недоступна"""
    mock_connect.side_effect = Exception("Database error")

    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["services"]["database"]["status"] == "unhealthy"
    assert "error" in data["services"]["database"]


@patch("app.api.v1.health.redis_client.ping")
def test_detailed_health_check_redis_failure(mock_ping, client):
    """Детальная проверка - Redis недоступен"""
    mock_ping.side_effect = Exception("Redis connection failed")

    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["services"]["redis"]["status"] == "unhealthy"
    assert "error" in data["services"]["redis"]


@patch("app.api.v1.health.celery_app.control.inspect")
def test_detailed_health_check_celery_no_workers(mock_inspect, client):
    """Детальная проверка - Celery воркеры не найдены"""
    mock_inspect_obj = MagicMock()
    mock_inspect_obj.active.return_value = None
    mock_inspect.return_value = mock_inspect_obj

    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "degraded"
    assert data["services"]["celery"]["status"] == "unhealthy"


@patch("app.api.v1.health.celery_app.control.inspect")
def test_detailed_health_check_celery_success(mock_inspect, client):
    """Детальная проверка - Celery работает"""
    mock_inspect_obj = MagicMock()
    mock_inspect_obj.active.return_value = {
        "worker1@localhost": [],
        "worker2@localhost": []
    }
    mock_inspect.return_value = mock_inspect_obj

    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()

    if data["services"]["celery"]["status"] == "healthy":
        assert data["services"]["celery"]["worker_count"] == 2
        assert "workers" in data["services"]["celery"]
