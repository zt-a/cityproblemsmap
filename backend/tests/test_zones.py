# tests/test_zones.py
import pytest

ZONES_URL    = "/api/v1/zones"
PROBLEMS_URL = "/api/v1/problems"
REGISTER_URL = "/api/v1/auth/register"

VALID_ZONE = {
    "name":       "Первомайский район",
    "zone_type":  "district",
    "country":    "Kyrgyzstan",
    "city":       "Bishkek",
    "center_lat": 42.8746,
    "center_lon": 74.5698,
}

VALID_PROBLEM = {
    "title":        "Яма на дороге",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "pothole",
    "nature":       "permanent",
}


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def created_zone(client, admin_headers):
    """Готовая зона созданная админом."""
    response = client.post(
        ZONES_URL + "/",
        json=VALID_ZONE,
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def child_zone(client, admin_headers, created_zone):
    """Дочерняя зона (квартал внутри района)."""
    response = client.post(
        ZONES_URL + "/",
        json={
            "name":              "Мкрн Восток-5",
            "zone_type":         "neighborhood",
            "country":           "Kyrgyzstan",
            "city":              "Bishkek",
            "parent_entity_id":  created_zone["entity_id"],
            "center_lat":        42.880,
            "center_lon":        74.575,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestCreateZone:

    def test_create_success(self, client, admin_headers):
        """Успешное создание зоны админом."""
        response = client.post(
            ZONES_URL + "/",
            json=VALID_ZONE,
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["name"]      == VALID_ZONE["name"]
        assert data["zone_type"] == VALID_ZONE["zone_type"]
        assert data["city"]      == VALID_ZONE["city"]
        assert data["version"]   == 1

        # Статистика при создании — всё нули
        assert data["total_problems"]  == 0
        assert data["open_problems"]   == 0
        assert data["pollution_index"] == 0.0
        assert data["risk_score"]      == 0.0

    def test_create_unauthorized(self, client):
        """Без токена — 401."""
        response = client.post(ZONES_URL + "/", json=VALID_ZONE)
        assert response.status_code == 401

    def test_create_by_regular_user_forbidden(self, client, auth_headers):
        """Обычный пользователь не может создавать зоны — 403."""
        response = client.post(
            ZONES_URL + "/",
            json=VALID_ZONE,
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_create_invalid_zone_type(self, client, admin_headers):
        """Невалидный zone_type — 422."""
        response = client.post(
            ZONES_URL + "/",
            json={**VALID_ZONE, "zone_type": "galaxy"},
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_create_short_name(self, client, admin_headers):
        """Слишком короткое название — 422."""
        response = client.post(
            ZONES_URL + "/",
            json={**VALID_ZONE, "name": "А"},
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_create_with_nonexistent_parent(self, client, admin_headers):
        """Несуществующая родительская зона — 404."""
        response = client.post(
            ZONES_URL + "/",
            json={**VALID_ZONE, "parent_entity_id": 99999},
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_create_with_valid_parent(self, client, admin_headers, created_zone):
        """Создание дочерней зоны с валидным parent_entity_id."""
        response = client.post(
            ZONES_URL + "/",
            json={
                **VALID_ZONE,
                "name":             "Квартал 5",
                "zone_type":        "neighborhood",
                "parent_entity_id": created_zone["entity_id"],
            },
            headers=admin_headers,
        )
        assert response.status_code == 201
        assert response.json()["parent_entity_id"] == created_zone["entity_id"]


class TestGetZone:

    def test_get_success(self, client, created_zone):
        """Получить зону по entity_id."""
        entity_id = created_zone["entity_id"]
        response  = client.get(f"{ZONES_URL}/{entity_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == entity_id
        assert data["name"]      == VALID_ZONE["name"]

    def test_get_not_found(self, client):
        """Несуществующая зона — 404."""
        response = client.get(f"{ZONES_URL}/99999")
        assert response.status_code == 404

    def test_get_unauthorized_allowed(self, client, created_zone):
        """Просмотр зоны доступен без авторизации."""
        response = client.get(f"{ZONES_URL}/{created_zone['entity_id']}")
        assert response.status_code == 200


class TestListZones:

    def test_list_empty(self, client):
        """Пустой список если нет зон."""
        response = client.get(ZONES_URL + "/")
        assert response.status_code == 200
        assert response.json()      == []

    def test_list_with_zones(self, client, created_zone):
        """После создания зоны список не пустой."""
        response = client.get(ZONES_URL + "/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_by_zone_type(self, client, created_zone):
        """Фильтр по zone_type."""
        response = client.get(
            ZONES_URL + "/",
            params={"zone_type": "district"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_zone_type_no_match(self, client, created_zone):
        """Фильтр по zone_type без совпадений — пустой список."""
        response = client.get(
            ZONES_URL + "/",
            params={"zone_type": "country"},
        )
        assert response.status_code == 200
        assert response.json()      == []

    def test_list_filter_by_city(self, client, created_zone):
        """Фильтр по городу."""
        response = client.get(
            ZONES_URL + "/",
            params={"city": "Bishkek"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_city_no_match(self, client, created_zone):
        """Фильтр по несуществующему городу — пустой список."""
        response = client.get(
            ZONES_URL + "/",
            params={"city": "Osh"},
        )
        assert response.status_code == 200
        assert response.json()      == []


class TestZoneChildren:

    def test_get_children(self, client, created_zone, child_zone):
        """Получить дочерние зоны."""
        entity_id = created_zone["entity_id"]
        response  = client.get(f"{ZONES_URL}/{entity_id}/children")

        assert response.status_code == 200
        children  = response.json()
        assert len(children)         == 1
        assert children[0]["name"]   == child_zone["name"]
        assert children[0]["parent_entity_id"] == entity_id

    def test_get_children_empty(self, client, created_zone):
        """Зона без дочерних — пустой список."""
        entity_id = created_zone["entity_id"]
        response  = client.get(f"{ZONES_URL}/{entity_id}/children")

        assert response.status_code == 200
        assert response.json()      == []


class TestZoneStats:

    def test_stats_empty_zone(self, client, created_zone):
        """Статистика пустой зоны — все нули."""
        entity_id = created_zone["entity_id"]
        response  = client.get(f"{ZONES_URL}/{entity_id}/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_problems"]  == 0
        assert data["solve_rate"]      == 0.0
        assert data["top_problem_types"] == []

    def test_stats_not_found(self, client):
        """Статистика несуществующей зоны — 404."""
        response = client.get(f"{ZONES_URL}/99999/stats")
        assert response.status_code == 404


class TestZoneProblems:

    def test_zone_problems_empty(self, client, created_zone):
        """Проблемы зоны — пустой список если нет проблем."""
        entity_id = created_zone["entity_id"]
        response  = client.get(f"{ZONES_URL}/{entity_id}/problems")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_zone_problems_not_found(self, client):
        """Проблемы несуществующей зоны — 404."""
        response = client.get(f"{ZONES_URL}/99999/problems")
        assert response.status_code == 404


class TestZoneHistory:

    def test_history_requires_admin(self, client, created_zone, auth_headers):
        """История зоны доступна только админу — 403 для обычного юзера."""
        entity_id = created_zone["entity_id"]
        response  = client.get(
            f"{ZONES_URL}/{entity_id}/history",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_history_admin_success(self, client, created_zone, admin_headers):
        """Админ видит историю зоны."""
        entity_id = created_zone["entity_id"]
        response  = client.get(
            f"{ZONES_URL}/{entity_id}/history",
            headers=admin_headers,
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history)          == 1
        assert history[0]["version"] == 1

    def test_history_not_found(self, client, admin_headers):
        """История несуществующей зоны — 404."""
        response = client.get(
            f"{ZONES_URL}/99999/history",
            headers=admin_headers,
        )
        assert response.status_code == 404


class TestZoneRecalculate:

    def test_recalculate_requires_admin(
        self, client, created_zone, auth_headers
    ):
        """Пересчёт доступен только админу."""
        entity_id = created_zone["entity_id"]
        response  = client.post(
            f"{ZONES_URL}/{entity_id}/recalculate",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_recalculate_success(self, client, created_zone, admin_headers):
        """
        Успешный пересчёт статистики зоны.
        Создаёт новую версию зоны.
        """
        entity_id = created_zone["entity_id"]
        response  = client.post(
            f"{ZONES_URL}/{entity_id}/recalculate",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # После пересчёта — новая версия
        assert data["version"]  == 2
        assert data["entity_id"] == entity_id

    def test_recalculate_not_found(self, client, admin_headers):
        """Пересчёт несуществующей зоны — 404."""
        response = client.post(
            f"{ZONES_URL}/99999/recalculate",
            headers=admin_headers,
        )
        assert response.status_code == 404