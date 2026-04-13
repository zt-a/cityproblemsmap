# tests/test_moderator.py
import pytest

MODERATOR_URL = "/api/v1/moderator"
REGISTER_URL = "/api/v1/auth/register"
ADMIN_URL = "/api/v1/admin"


@pytest.fixture
def moderator_user(client, admin_headers):
    """Создаём модератора через admin."""
    reg = client.post(REGISTER_URL, json={
        "username": "moderatoruser",
        "email": "moderator@test.com",
        "password": "password123",
        "city": "Bishkek",
    }).json()

    # Даём роль moderator
    client.patch(
        f"{ADMIN_URL}/users/{reg['user']['entity_id']}/role",
        json={"role": "moderator"},
        headers=admin_headers,
    )
    return reg


@pytest.fixture
def moderator_headers(moderator_user):
    return {"Authorization": f"Bearer {moderator_user['access_token']}"}


def test_get_flagged_comments(client, moderator_headers):
    """Модератор видит комментарии с жалобами."""
    response = client.get(
        f"{MODERATOR_URL}/comments/flagged",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_suspicious_problems(client, moderator_headers):
    """Модератор видит подозрительные проблемы с низким truth_score."""
    response = client.get(
        f"{MODERATOR_URL}/problems/suspicious?threshold=0.5",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_pending_problems(client, moderator_headers):
    """Модератор видит новые проблемы требующие проверки."""
    response = client.get(
        f"{MODERATOR_URL}/problems/pending?hours=24",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_moderator_stats(client, moderator_headers):
    """Модератор может видеть свою статистику."""
    response = client.get(
        f"{MODERATOR_URL}/stats",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "problems_verified" in data
    assert "problems_rejected" in data
    assert "comments_hidden" in data
    assert "users_suspended" in data
    assert "flagged_pending" in data
    assert "suspicious_pending" in data


def test_regular_user_cannot_access_moderator_panel(client, auth_headers):
    """Обычный пользователь не может получить доступ к панели модератора."""
    response = client.get(
        f"{MODERATOR_URL}/stats",
        headers=auth_headers,
    )
    assert response.status_code == 403
