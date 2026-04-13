# tests/test_simulation.py
import pytest

SIMULATIONS_URL = "/api/v1/simulations"
ZONES_URL       = "/api/v1/zones"

VALID_ZONE = {
    "name":       "Первомайский район",
    "zone_type":  "district",
    "country":    "Kyrgyzstan",
    "city":       "Bishkek",
    "center_lat": 42.8746,
    "center_lon": 74.5698,
}

VALID_EVENT = {
    "event_type":      "road_repair",
    "title":           "Ремонт дороги на ул. Манаса",
    "description":     "Плановый ремонт асфальтового покрытия",
    "traffic_impact":  0.3,
    "pollution_impact": 0.1,
    "risk_delta":      0.05,
}


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def created_zone(client, admin_headers):
    response = client.post(
        ZONES_URL + "/",
        json=VALID_ZONE,
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_event(client, admin_headers, created_zone):
    """Готовое событие со статусом planned."""
    response = client.post(
        SIMULATIONS_URL + "/",
        json={**VALID_EVENT, "zone_entity_id": created_zone["entity_id"]},
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestCreateEvent:

    def test_create_success(self, client, admin_headers, created_zone):
        """Успешное создание события админом."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={**VALID_EVENT, "zone_entity_id": created_zone["entity_id"]},
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["title"]           == VALID_EVENT["title"]
        assert data["event_type"]      == VALID_EVENT["event_type"]
        assert data["status"]          == "planned"   # всегда planned при создании
        assert data["version"]         == 1
        assert data["traffic_impact"]  == VALID_EVENT["traffic_impact"]
        assert data["zone_entity_id"]  == created_zone["entity_id"]

    def test_create_unauthorized(self, client, created_zone):
        """Без токена — 401."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={**VALID_EVENT, "zone_entity_id": created_zone["entity_id"]},
        )
        assert response.status_code == 401

    def test_create_by_regular_user_forbidden(
        self, client, auth_headers, created_zone
    ):
        """Обычный пользователь не может создавать события — 403."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={**VALID_EVENT, "zone_entity_id": created_zone["entity_id"]},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_create_nonexistent_zone(self, client, admin_headers):
        """Несуществующая зона — 404."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={**VALID_EVENT, "zone_entity_id": 99999},
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_create_invalid_event_type(
        self, client, admin_headers, created_zone
    ):
        """Невалидный event_type — 422."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={
                **VALID_EVENT,
                "zone_entity_id": created_zone["entity_id"],
                "event_type":     "alien_invasion",
            },
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_create_invalid_impact_range(
        self, client, admin_headers, created_zone
    ):
        """Impact вне диапазона -1.0..+1.0 — 422."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={
                **VALID_EVENT,
                "zone_entity_id": created_zone["entity_id"],
                "traffic_impact": 2.0,  # максимум 1.0
            },
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_create_short_title(self, client, admin_headers, created_zone):
        """Короткий заголовок — 422."""
        response = client.post(
            SIMULATIONS_URL + "/",
            json={
                **VALID_EVENT,
                "zone_entity_id": created_zone["entity_id"],
                "title":          "Яма",
            },
            headers=admin_headers,
        )
        assert response.status_code == 422


class TestGetEvent:

    def test_get_success(self, client, created_event):
        """Получить событие по entity_id."""
        entity_id = created_event["entity_id"]
        response  = client.get(f"{SIMULATIONS_URL}/{entity_id}")

        assert response.status_code == 200
        assert response.json()["entity_id"] == entity_id

    def test_get_not_found(self, client):
        """Несуществующее событие — 404."""
        response = client.get(f"{SIMULATIONS_URL}/99999")
        assert response.status_code == 404

    def test_get_unauthorized_allowed(self, client, created_event):
        """Просмотр доступен без авторизации."""
        response = client.get(
            f"{SIMULATIONS_URL}/{created_event['entity_id']}"
        )
        assert response.status_code == 200


class TestListEvents:

    def test_list_empty(self, client):
        """Пустой список если нет событий."""
        response = client.get(SIMULATIONS_URL + "/")
        assert response.status_code == 200
        assert response.json()      == []

    def test_list_with_event(self, client, created_event):
        """После создания события список не пустой."""
        response = client.get(SIMULATIONS_URL + "/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_by_zone(self, client, created_event, created_zone):
        """Фильтр по zone_entity_id."""
        response = client.get(
            SIMULATIONS_URL + "/",
            params={"zone_entity_id": created_zone["entity_id"]},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_zone_no_match(self, client, created_event):
        """Фильтр по несуществующей зоне — пустой список."""
        response = client.get(
            SIMULATIONS_URL + "/",
            params={"zone_entity_id": 99999},
        )
        assert response.status_code == 200
        assert response.json()      == []

    def test_list_filter_by_status(self, client, created_event):
        """Фильтр по статусу planned."""
        response = client.get(
            SIMULATIONS_URL + "/",
            params={"status": "planned"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_filter_status_no_match(self, client, created_event):
        """Фильтр по статусу active — нет таких событий."""
        response = client.get(
            SIMULATIONS_URL + "/",
            params={"status": "active"},
        )
        assert response.status_code == 200
        assert response.json()      == []


class TestUpdateEventStatus:

    def test_planned_to_active(
        self, client, created_event, created_zone, admin_headers
    ):
        """
        planned → active.
        Создаёт новую версию события.
        Применяет дельты к индексам зоны.
        """
        entity_id = created_event["entity_id"]
        response  = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"]       == "active"
        assert data["version"]      == 2
        assert data["actual_start"] is not None

        # Проверяем что индексы зоны изменились
        zone = client.get(
            f"{ZONES_URL}/{created_zone['entity_id']}"
        ).json()
        assert zone["traffic_index"]   > 0.0
        assert zone["pollution_index"] > 0.0

    def test_active_to_completed(
        self, client, created_event, created_zone, admin_headers
    ):
        """
        active → completed.
        Откатывает дельты — индексы зоны возвращаются к исходным.
        """
        entity_id = created_event["entity_id"]

        # planned → active
        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )

        # Запоминаем индексы после активации
        zone_active = client.get(
            f"{ZONES_URL}/{created_zone['entity_id']}"
        ).json()

        # active → completed
        response = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "completed"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"]  == "completed"
        assert response.json()["version"] == 3

        # Индексы откатились
        zone_completed = client.get(
            f"{ZONES_URL}/{created_zone['entity_id']}"
        ).json()
        assert zone_completed["traffic_index"]   < zone_active["traffic_index"]
        assert zone_completed["pollution_index"] < zone_active["pollution_index"]

    def test_active_to_cancelled(
        self, client, created_event, admin_headers
    ):
        """active → cancelled — тоже откатывает дельты."""
        entity_id = created_event["entity_id"]

        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        response = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "cancelled"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_planned_to_cancelled(
        self, client, created_event, created_zone, admin_headers
    ):
        """
        planned → cancelled.
        Дельты НЕ применялись — индексы зоны не меняются.
        """
        entity_id = created_event["entity_id"]

        zone_before = client.get(
            f"{ZONES_URL}/{created_zone['entity_id']}"
        ).json()

        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "cancelled"},
            headers=admin_headers,
        )

        zone_after = client.get(
            f"{ZONES_URL}/{created_zone['entity_id']}"
        ).json()

        # Индексы не должны измениться
        assert zone_after["traffic_index"]   == zone_before["traffic_index"]
        assert zone_after["pollution_index"] == zone_before["pollution_index"]

    def test_invalid_transition_completed_to_active(
        self, client, created_event, admin_headers
    ):
        """
        completed → active — невалидный переход — 400.
        completed это финальный статус.
        """
        entity_id = created_event["entity_id"]

        # Доводим до completed
        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "completed"},
            headers=admin_headers,
        )

        # Пытаемся вернуть в active
        response = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_invalid_transition_planned_to_completed(
        self, client, created_event, admin_headers
    ):
        """planned → completed — невалидный переход — 400."""
        entity_id = created_event["entity_id"]
        response  = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "completed"},
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_update_unauthorized(self, client, created_event):
        """Без токена — 401."""
        entity_id = created_event["entity_id"]
        response  = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
        )
        assert response.status_code == 401

    def test_update_by_regular_user_forbidden(
        self, client, created_event, auth_headers
    ):
        """Обычный пользователь не может менять статус — 403."""
        entity_id = created_event["entity_id"]
        response  = client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_update_not_found(self, client, admin_headers):
        """Несуществующее событие — 404."""
        response = client.patch(
            f"{SIMULATIONS_URL}/99999/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        assert response.status_code == 404


class TestEventHistory:

    def test_history_initial(self, client, created_event, admin_headers):
        """После создания — одна версия в истории."""
        entity_id = created_event["entity_id"]
        response  = client.get(
            f"{SIMULATIONS_URL}/{entity_id}/history",
            headers=admin_headers,
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history)          == 1
        assert history[0]["version"] == 1
        assert history[0]["status"]  == "planned"

    def test_history_after_transitions(
        self, client, created_event, admin_headers
    ):
        """
        После двух переходов — три версии в истории.
        planned → active → completed = 3 версии.
        """
        entity_id = created_event["entity_id"]

        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "active"},
            headers=admin_headers,
        )
        client.patch(
            f"{SIMULATIONS_URL}/{entity_id}/status",
            json={"status": "completed"},
            headers=admin_headers,
        )

        response = client.get(
            f"{SIMULATIONS_URL}/{entity_id}/history",
            headers=admin_headers,
        )
        history = response.json()

        assert len(history)          == 3
        assert history[0]["status"]  == "planned"
        assert history[1]["status"]  == "active"
        assert history[2]["status"]  == "completed"

    def test_history_unauthorized(self, client, created_event):
        """Без токена — 401."""
        entity_id = created_event["entity_id"]
        response  = client.get(
            f"{SIMULATIONS_URL}/{entity_id}/history"
        )
        assert response.status_code == 401

    def test_history_by_regular_user_forbidden(
        self, client, created_event, auth_headers
    ):
        """Обычный пользователь не видит историю — 403."""
        entity_id = created_event["entity_id"]
        response  = client.get(
            f"{SIMULATIONS_URL}/{entity_id}/history",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_history_not_found(self, client, admin_headers):
        """История несуществующего события — 404."""
        response = client.get(
            f"{SIMULATIONS_URL}/99999/history",
            headers=admin_headers,
        )
        assert response.status_code == 404


class TestPreviewImpact:

    def test_preview_success(self, client, created_zone, admin_headers):
        """Успешный предпросмотр влияния события."""
        response = client.post(
            SIMULATIONS_URL + "/preview",
            params={
                "zone_entity_id":  created_zone["entity_id"],
                "traffic_impact":  0.3,
                "pollution_impact": 0.1,
                "risk_delta":      0.05,
            },
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["zone_entity_id"]      == created_zone["entity_id"]
        assert data["zone_name"]           == VALID_ZONE["name"]
        assert data["projected_traffic"]   > data["current_traffic_index"]
        assert data["projected_pollution"] > data["current_pollution_index"]
        assert "delta_summary"             in data
        assert len(data["delta_summary"])  > 0

    def test_preview_negative_impact(self, client, created_zone, admin_headers):
        """
        Отрицательный impact = улучшение.
        projected < current.
        """
        response = client.post(
            SIMULATIONS_URL + "/preview",
            params={
                "zone_entity_id":  created_zone["entity_id"],
                "traffic_impact":  -0.2,   # трафик улучшится
                "pollution_impact": 0.0,
                "risk_delta":      0.0,
            },
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Трафик улучшился — projected меньше или равен current
        assert data["projected_traffic"] <= data["current_traffic_index"]

    def test_preview_nonexistent_zone(self, client, admin_headers):
        """Превью для несуществующей зоны — 404."""
        response = client.post(
            SIMULATIONS_URL + "/preview",
            params={
                "zone_entity_id": 99999,
                "traffic_impact": 0.3,
            },
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_preview_unauthorized(self, client, created_zone):
        """Без токена — 401."""
        response = client.post(
            SIMULATIONS_URL + "/preview",
            params={
                "zone_entity_id": created_zone["entity_id"],
                "traffic_impact": 0.3,
            },
        )
        assert response.status_code == 401

    def test_preview_by_regular_user_forbidden(
        self, client, created_zone, auth_headers
    ):
        """Обычный пользователь не может смотреть превью — 403."""
        response = client.post(
            SIMULATIONS_URL + "/preview",
            params={
                "zone_entity_id": created_zone["entity_id"],
                "traffic_impact": 0.3,
            },
            headers=auth_headers,
        )
        assert response.status_code == 403