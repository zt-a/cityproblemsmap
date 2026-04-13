# tests/test_user_settings.py
import pytest
from fastapi.testclient import TestClient


def test_get_notification_settings_creates_default(client: TestClient, auth_headers):
    """Тест получения настроек уведомлений (создаются по умолчанию)"""
    response = client.get("/api/v1/settings/notifications", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email_enabled"] == True
    assert data["push_enabled"] == True
    assert data["digest_frequency"] == "daily"
    assert data["quiet_hours_enabled"] == False


def test_update_notification_settings(client: TestClient, auth_headers):
    """Тест обновления настроек уведомлений"""
    # Сначала получаем настройки (создаются автоматически)
    response = client.get("/api/v1/settings/notifications", headers=auth_headers)
    assert response.status_code == 200

    # Обновляем настройки
    update_data = {
        "email_enabled": False,
        "push_enabled": True,
        "digest_frequency": "weekly",
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22",
        "quiet_hours_end": "8",
    }

    response = client.patch(
        "/api/v1/settings/notifications",
        json=update_data,
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["email_enabled"] == False
    assert data["push_enabled"] == True
    assert data["digest_frequency"] == "weekly"
    assert data["quiet_hours_enabled"] == True
    assert data["quiet_hours_start"] == 22
    assert data["quiet_hours_end"] == 8


def test_update_notification_settings_partial(client: TestClient, auth_headers):
    """Тест частичного обновления настроек"""
    # Получаем настройки
    client.get("/api/v1/settings/notifications", headers=auth_headers)

    # Обновляем только email_enabled
    response = client.patch(
        "/api/v1/settings/notifications",
        json={"email_enabled": False},
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["email_enabled"] == False
    # Остальные поля должны остаться по умолчанию
    assert data["push_enabled"] == True


def test_update_notification_settings_empty(client: TestClient, auth_headers):
    """Тест обновления с пустыми данными"""
    # Получаем настройки
    response = client.get("/api/v1/settings/notifications", headers=auth_headers)
    original_data = response.json()

    # Отправляем пустое обновление
    response = client.patch(
        "/api/v1/settings/notifications",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Данные не должны измениться
    data = response.json()
    assert data["email_enabled"] == original_data["email_enabled"]


def test_get_notification_settings_unauthorized(client: TestClient):
    """Тест получения настроек без авторизации"""
    response = client.get("/api/v1/settings/notifications")
    assert response.status_code == 401


def test_update_notification_settings_unauthorized(client: TestClient):
    """Тест обновления настроек без авторизации"""
    response = client.patch(
        "/api/v1/settings/notifications",
        json={"email_enabled": False},
    )
    assert response.status_code == 401


def test_notification_settings_versioning(client: TestClient, auth_headers):
    """Тест версионирования настроек"""
    from app.database import SessionLocal
    from app.models.user_settings import UserNotificationSettings

    # Получаем настройки
    client.get("/api/v1/settings/notifications", headers=auth_headers)

    # Обновляем несколько раз
    client.patch(
        "/api/v1/settings/notifications",
        json={"email_enabled": False},
        headers=auth_headers,
    )

    client.patch(
        "/api/v1/settings/notifications",
        json={"push_enabled": False},
        headers=auth_headers,
    )

    # Проверяем что создались версии
    db = SessionLocal()
    try:
        # settings = db.query(UserNotificationSettings).filter_by(
        #     entity_id=1
        # ).all()
        from app.models.user import User
        user = db.query(User).filter_by(is_current=True).first()
        settings = db.query(UserNotificationSettings).filter_by(
            user_entity_id=user.entity_id
        ).all()

        # Должно быть 3 версии (создание + 2 обновления)
        assert len(settings) == 3

        # Только последняя версия is_current
        current_versions = [s for s in settings if s.is_current]
        assert len(current_versions) == 1

        # Проверяем версии
        versions = sorted(settings, key=lambda x: x.version)
        assert versions[0].version == 1
        assert versions[1].version == 2
        assert versions[2].version == 3

        # Последняя версия должна иметь оба изменения
        assert not versions[2].email_enabled 
        assert not versions[2].push_enabled
    finally:
        db.close()
