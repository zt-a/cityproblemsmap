# tests/test_official.py
import pytest

OFFICIAL_URL = "/api/v1/official"
REGISTER_URL = "/api/v1/auth/register"
ADMIN_URL = "/api/v1/admin"


@pytest.fixture
def official_user(client, admin_headers):
    """Создаём официала через admin."""
    reg = client.post(REGISTER_URL, json={
        "username": "officialuser",
        "email": "official@test.com",
        "password": "password123",
        "city": "Bishkek",
    }).json()

    # Даём роль official
    client.patch(
        f"{ADMIN_URL}/users/{reg['user']['entity_id']}/role",
        json={"role": "official"},
        headers=admin_headers,
    )
    return reg


@pytest.fixture
def official_headers(official_user):
    return {"Authorization": f"Bearer {official_user['access_token']}"}


def test_get_assigned_problems(client, official_headers):
    """Официал видит назначенные на него проблемы."""
    response = client.get(
        f"{OFFICIAL_URL}/problems/assigned",
        headers=official_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_in_progress_problems(client, official_headers):
    """Официал видит проблемы в работе."""
    response = client.get(
        f"{OFFICIAL_URL}/problems/in-progress",
        headers=official_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_get_official_zones(client, official_headers):
    """Официал видит зоны своего города."""
    response = client.get(
        f"{OFFICIAL_URL}/zones",
        headers=official_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_official_stats(client, official_headers):
    """Официал может видеть свою статистику."""
    response = client.get(
        f"{OFFICIAL_URL}/stats",
        headers=official_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "problems_assigned" in data
    assert "problems_in_progress" in data
    assert "problems_resolved" in data
    assert "avg_resolution_days" in data
    assert "zones_managed" in data
    assert "official_responses" in data


def test_regular_user_cannot_access_official_panel(client, auth_headers):
    """Обычный пользователь не может получить доступ к панели официала."""
    response = client.get(
        f"{OFFICIAL_URL}/stats",
        headers=auth_headers,
    )
    assert response.status_code == 403
