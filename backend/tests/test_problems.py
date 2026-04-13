# tests/test_problems.py
import pytest

PROBLEMS_URL = "/api/v1/problems"

VALID_PROBLEM = {
    "title":        "Яма на дороге",
    "description":  "Большая яма на пересечении улиц",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "district":     "Первомайский",
    "address":      "ул. Манаса 50",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "pothole",
    "nature":       "permanent",
    "tags":         ["asphalt", "road"],
}


# ── Фикстура: готовая проблема в БД ──────────────────────
@pytest.fixture
def created_problem(client, auth_headers):
    """Создаёт проблему и возвращает её данные."""
    response = client.post(
        PROBLEMS_URL + "/",
        json=VALID_PROBLEM,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


# ── Второй пользователь (для тестов голосования и прав) ──
@pytest.fixture
def second_user(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "seconduser",
        "email":    "second@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    token = second_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestCreateProblem:

    def test_create_success(self, client, auth_headers):
        """Успешное создание проблемы."""
        response = client.post(
            PROBLEMS_URL + "/",
            json=VALID_PROBLEM,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["title"]        == VALID_PROBLEM["title"]
        assert data["city"]         == VALID_PROBLEM["city"]
        assert data["problem_type"] == VALID_PROBLEM["problem_type"]
        assert data["status"]       == "open"
        assert data["version"]      == 1
        assert data["latitude"]     == VALID_PROBLEM["latitude"]
        assert data["longitude"]    == VALID_PROBLEM["longitude"]
        assert data["tags"]         == VALID_PROBLEM["tags"]

        # Scores при создании = 0
        assert data["truth_score"]   == 0.0
        assert data["priority_score"] == 0.0

    def test_create_unauthorized(self, client):
        """Без токена — 401."""
        response = client.post(PROBLEMS_URL + "/", json=VALID_PROBLEM)
        assert response.status_code == 401

    def test_create_wrong_city(self, client, auth_headers):
        """
        Пользователь из Bishkek пытается создать проблему в Оше — 403.
        Геопроверка: user.city != problem.city
        """
        response = client.post(
            PROBLEMS_URL + "/",
            json={**VALID_PROBLEM, "city": "Osh"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_create_short_title(self, client, auth_headers):
        """Заголовок меньше 5 символов — 422."""
        response = client.post(
            PROBLEMS_URL + "/",
            json={**VALID_PROBLEM, "title": "Яма"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_invalid_coordinates(self, client, auth_headers):
        """Невалидные координаты — 422."""
        response = client.post(
            PROBLEMS_URL + "/",
            json={**VALID_PROBLEM, "latitude": 999.0},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_invalid_problem_type(self, client, auth_headers):
        """Несуществующий тип проблемы — 422."""
        response = client.post(
            PROBLEMS_URL + "/",
            json={**VALID_PROBLEM, "problem_type": "flying_saucer"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestGetProblem:

    def test_get_success(self, client, created_problem):
        """Получить проблему по entity_id."""
        entity_id = created_problem["entity_id"]
        response  = client.get(f"{PROBLEMS_URL}/{entity_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == entity_id
        assert data["title"]     == VALID_PROBLEM["title"]

    def test_get_not_found(self, client):
        """Несуществующий entity_id — 404."""
        response = client.get(f"{PROBLEMS_URL}/99999")
        assert response.status_code == 404

    def test_get_unauthorized_allowed(self, client, created_problem):
        """Просмотр проблемы доступен без авторизации."""
        entity_id = created_problem["entity_id"]
        response  = client.get(f"{PROBLEMS_URL}/{entity_id}")
        assert response.status_code == 200


class TestListProblems:

    def test_list_empty(self, client):
        """Пустой список если нет проблем."""
        response = client.get(PROBLEMS_URL + "/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_with_problems(self, client, created_problem):
        """После создания проблемы список не пустой."""
        response = client.get(PROBLEMS_URL + "/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_list_filter_by_city(self, client, created_problem):
        """Фильтр по городу."""
        response = client.get(
            PROBLEMS_URL + "/",
            params={"city": "Bishkek"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_filter_city_no_match(self, client, created_problem):
        """Фильтр по городу где нет проблем — пустой список."""
        response = client.get(
            PROBLEMS_URL + "/",
            params={"city": "Osh"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_list_filter_by_type(self, client, created_problem):
        """Фильтр по типу проблемы."""
        response = client.get(
            PROBLEMS_URL + "/",
            params={"problem_type": "pothole"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_filter_by_status(self, client, created_problem):
        """Фильтр по статусу."""
        response = client.get(
            PROBLEMS_URL + "/",
            params={"status": "open"},
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_list_pagination(self, client, auth_headers):
        """Пагинация — limit и offset работают."""
        # Создаём 3 проблемы
        for i in range(3):
            client.post(
                PROBLEMS_URL + "/",
                json={**VALID_PROBLEM, "title": f"Проблема номер {i + 1}"},
                headers=auth_headers,
            )

        # Запрашиваем только первые 2
        response = client.get(
            PROBLEMS_URL + "/",
            params={"limit": 2, "offset": 0},
        )
        data = response.json()
        assert data["total"]      == 3
        assert len(data["items"]) == 2

        # Запрашиваем с offset=2 — должна быть одна оставшаяся
        response = client.get(
            PROBLEMS_URL + "/",
            params={"limit": 2, "offset": 2},
        )
        data = response.json()
        assert len(data["items"]) == 1


class TestProblemHistory:

    def test_history_initial(self, client, created_problem):
        """
        После создания у проблемы одна версия.
        history возвращает список из одного элемента.
        """
        entity_id = created_problem["entity_id"]
        response  = client.get(f"{PROBLEMS_URL}/{entity_id}/history")

        assert response.status_code == 200
        history = response.json()
        assert len(history) == 1
        assert history[0]["version"] == 1

    def test_history_after_status_update(
        self, client, created_problem, auth_headers
    ):
        """
        После смены статуса — две версии в истории.
        Версионирование работает.
        """
        entity_id = created_problem["entity_id"]

        # Меняем статус
        client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        response = client.get(f"{PROBLEMS_URL}/{entity_id}/history")
        history  = response.json()

        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[0]["status"]  == "open"
        assert history[1]["version"] == 2
        assert history[1]["status"]  == "in_progress"

    def test_history_not_found(self, client):
        """История несуществующей проблемы — 404."""
        response = client.get(f"{PROBLEMS_URL}/99999/history")
        assert response.status_code == 404


class TestUpdateProblemStatus:

    def test_author_can_update_status(
        self, client, created_problem, auth_headers
    ):
        """Автор может сменить статус своей проблемы."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"]  == "in_progress"
        assert response.json()["version"] == 2  # новая версия

    def test_solved_sets_resolved_fields(
        self, client, created_problem, auth_headers
    ):
        """
        При статусе solved — заполняются resolved_by_entity_id и resolved_at.
        """
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={
                "status":          "solved",
                "resolution_note": "Яму заделали",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"]                == "solved"
        assert data["resolved_by_entity_id"] is not None
        assert data["resolved_at"]           is not None
        assert data["resolution_note"]       == "Яму заделали"

    def test_stranger_cannot_update_status(
        self, client, created_problem, second_headers
    ):
        """
        Другой пользователь (не автор, не модератор) не может менять статус — 403.
        """
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "in_progress"},
            headers=second_headers,
        )
        assert response.status_code == 403

    def test_update_status_unauthorized(self, client, created_problem):
        """Без токена — 401."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "in_progress"},
        )
        assert response.status_code == 401

    def test_update_status_not_found(self, client, auth_headers):
        """Несуществующая проблема — 404."""
        response = client.patch(
            f"{PROBLEMS_URL}/99999/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_status_creates_new_version(
        self, client, created_problem, auth_headers
    ):
        """
        Каждая смена статуса = новая версия.
        open → in_progress → solved = 3 версии в истории.
        """
        entity_id = created_problem["entity_id"]

        client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        client.patch(
            f"{PROBLEMS_URL}/{entity_id}/status",
            json={"status": "solved"},
            headers=auth_headers,
        )

        history = client.get(
            f"{PROBLEMS_URL}/{entity_id}/history"
        ).json()

        assert len(history) == 3
        assert history[0]["status"] == "open"
        assert history[1]["status"] == "in_progress"
        assert history[2]["status"] == "solved"