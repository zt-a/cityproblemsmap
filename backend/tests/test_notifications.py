# tests/test_notifications.py
import pytest
from app.models.notification import NotificationType


NOTIFICATIONS_URL = "/api/v1/notifications"


def test_get_notifications_empty(client, auth_headers):
    """Тест получения пустого списка уведомлений"""
    response = client.get(NOTIFICATIONS_URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert len(data["notifications"]) == 0


def test_notification_stats(client, auth_headers):
    """Тест получения статистики уведомлений"""
    response = client.get(f"{NOTIFICATIONS_URL}/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unread" in data
    assert "by_type" in data


def test_mark_all_as_read(client, auth_headers):
    """Тест отметки всех уведомлений как прочитанных"""
    response = client.post(f"{NOTIFICATIONS_URL}/mark-all-read", headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()


def test_get_notifications_with_filters(client, auth_headers):
    """Тест получения уведомлений с фильтрами"""
    # Только непрочитанные
    response = client.get(
        NOTIFICATIONS_URL,
        params={"unread_only": True},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # По типу
    response = client.get(
        NOTIFICATIONS_URL,
        params={"notification_type": NotificationType.PROBLEM_COMMENTED},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_delete_all_notifications(client, auth_headers):
    """Тест удаления всех уведомлений"""
    response = client.delete(NOTIFICATIONS_URL, headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()
