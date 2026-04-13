# tests/test_admin.py
import pytest

ADMIN_URL    = "/api/v1/admin"
PROBLEMS_URL = "/api/v1/problems"
REGISTER_URL = "/api/v1/auth/register"


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def second_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "regularuser",
        "email":    "regular@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    return {"Authorization": f"Bearer {second_user['access_token']}"}


@pytest.fixture
def moderator_user(client, admin_headers):
    """Создаём модератора через admin."""
    # Сначала регистрируем
    reg = client.post(REGISTER_URL, json={
        "username": "moderatoruser",
        "email":    "moderator@test.com",
        "password": "password123",
        "city":     "Bishkek",
    }).json()

    # Даём роль moderator
    client.patch(
        f"{ADMIN_URL}/users/{reg['user']['entity_id']}/role",
        json    = {"role": "moderator"},
        headers = admin_headers,
    )
    return reg


@pytest.fixture
def moderator_headers(moderator_user):
    return {"Authorization": f"Bearer {moderator_user['access_token']}"}


@pytest.fixture
def created_problem(client, auth_headers):
    response = client.post(PROBLEMS_URL + "/", json={
        "title":        "Тестовая проблема",
        "country":      "Kyrgyzstan",
        "city":         "Bishkek",
        "latitude":     42.8746,
        "longitude":    74.5698,
        "problem_type": "pothole",
        "nature":       "permanent",
    }, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


# ══════════════════════════════════════════════════════════
# ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ
# ══════════════════════════════════════════════════════════

class TestListUsers:

    def test_admin_can_list_users(self, client, admin_headers, registered_user):
        """Админ видит список пользователей."""
        response = client.get(
            f"{ADMIN_URL}/users",
            headers = admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert "items" in data

    def test_moderator_can_list_users(
        self, client, moderator_headers, registered_user
    ):
        """Модератор тоже видит список."""
        response = client.get(
            f"{ADMIN_URL}/users",
            headers = moderator_headers,
        )
        assert response.status_code == 200

    def test_regular_user_cannot_list(self, client, auth_headers):
        """Обычный пользователь — 403."""
        response = client.get(
            f"{ADMIN_URL}/users",
            headers = auth_headers,
        )
        assert response.status_code == 403

    def test_unauthorized_cannot_list(self, client):
        """Без токена — 401."""
        response = client.get(f"{ADMIN_URL}/users")
        assert response.status_code == 401

    def test_filter_by_role(self, client, admin_headers, registered_user):
        """Фильтр по роли."""
        response = client.get(
            f"{ADMIN_URL}/users",
            params  = {"role": "user"},
            headers = admin_headers,
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(u["role"] == "user" for u in items)

    def test_filter_by_status(self, client, admin_headers, registered_user):
        """Фильтр по статусу."""
        response = client.get(
            f"{ADMIN_URL}/users",
            params  = {"status": "active"},
            headers = admin_headers,
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(u["status"] == "active" for u in items)

    def test_search_by_username(self, client, admin_headers, registered_user):
        """Поиск по username."""
        response = client.get(
            f"{ADMIN_URL}/users",
            params  = {"search": "testuser"},
            headers = admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1


class TestGetUserAdmin:

    def test_get_user_success(self, client, admin_headers, registered_user):
        """Получить пользователя по entity_id."""
        entity_id = registered_user["user"]["entity_id"]
        response  = client.get(
            f"{ADMIN_URL}/users/{entity_id}",
            headers = admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == entity_id
        assert "email" in data   # email виден в admin view

    def test_get_user_not_found(self, client, admin_headers):
        """Несуществующий пользователь — 404."""
        response = client.get(
            f"{ADMIN_URL}/users/99999",
            headers = admin_headers,
        )
        assert response.status_code == 404


class TestChangeRole:

    def test_admin_can_change_role(
        self, client, admin_headers, second_user
    ):
        """Админ меняет роль пользователя."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "moderator"},
            headers = admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["role"]    == "moderator"
        assert response.json()["version"] == 2

    def test_cannot_change_own_role(self, client, admin_headers, registered_admin):
        """Нельзя менять роль самому себе — 400."""
        entity_id = registered_admin["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "user"},
            headers = admin_headers,
        )
        assert response.status_code == 400

    def test_same_role_fails(self, client, admin_headers, second_user):
        """Та же роль — 400."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "user"},   # уже user
            headers = admin_headers,
        )
        assert response.status_code == 400

    def test_moderator_cannot_change_role(
        self, client, moderator_headers, second_user
    ):
        """Модератор не может менять роли — только admin."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "moderator"},
            headers = moderator_headers,
        )
        assert response.status_code == 403

    def test_invalid_role(self, client, admin_headers, second_user):
        """Невалидная роль — 422."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "superadmin"},
            headers = admin_headers,
        )
        assert response.status_code == 422


class TestSuspendUser:

    def test_moderator_can_suspend(
        self, client, moderator_headers, second_user
    ):
        """Модератор блокирует обычного пользователя."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Спам"},
            headers = moderator_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "suspended"

    def test_cannot_suspend_self(self, client, moderator_headers, moderator_user):
        """Нельзя заблокировать самого себя — 400."""
        entity_id = moderator_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Тест"},
            headers = moderator_headers,
        )
        assert response.status_code == 400

    def test_moderator_cannot_suspend_admin(
        self, client, moderator_headers, registered_admin
    ):
        """Модератор не может заблокировать админа — 403."""
        entity_id = registered_admin["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Тест"},
            headers = moderator_headers,
        )
        assert response.status_code == 403

    def test_already_suspended(
        self, client, moderator_headers, second_user
    ):
        """Повторная блокировка — 400."""
        entity_id = second_user["user"]["entity_id"]

        client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Первая"},
            headers = moderator_headers,
        )
        response = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Вторая"},
            headers = moderator_headers,
        )
        assert response.status_code == 400

    def test_regular_user_cannot_suspend(
        self, client, auth_headers, second_user
    ):
        """Обычный пользователь не может блокировать — 403."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Тест"},
            headers = auth_headers,
        )
        assert response.status_code == 403


class TestUnsuspendUser:

    def test_unsuspend_success(
        self, client, moderator_headers, second_user
    ):
        """Успешное снятие блокировки."""
        entity_id = second_user["user"]["entity_id"]

        # Блокируем
        client.patch(
            f"{ADMIN_URL}/users/{entity_id}/suspend",
            json    = {"reason": "Тест"},
            headers = moderator_headers,
        )

        # Снимаем
        response = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/unsuspend",
            headers = moderator_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_unsuspend_active_user(
        self, client, moderator_headers, second_user
    ):
        """Снять блокировку с активного — 400."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/users/{entity_id}/unsuspend",
            headers = moderator_headers,
        )
        assert response.status_code == 400


class TestUserHistory:

    def test_admin_sees_history(
        self, client, admin_headers, second_user
    ):
        """Админ видит историю версий пользователя."""
        entity_id = second_user["user"]["entity_id"]

        # Меняем роль — создаём версию
        client.patch(
            f"{ADMIN_URL}/users/{entity_id}/role",
            json    = {"role": "volunteer"},
            headers = admin_headers,
        )

        response = client.get(
            f"{ADMIN_URL}/users/{entity_id}/history",
            headers = admin_headers,
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history)          >= 2
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2

    def test_moderator_cannot_see_history(
        self, client, moderator_headers, second_user
    ):
        """Модератор не видит историю — только admin."""
        entity_id = second_user["user"]["entity_id"]
        response  = client.get(
            f"{ADMIN_URL}/users/{entity_id}/history",
            headers = moderator_headers,
        )
        assert response.status_code == 403


# ══════════════════════════════════════════════════════════
# ТЕСТЫ ПРОБЛЕМ
# ══════════════════════════════════════════════════════════

class TestAdminProblems:

    def test_list_problems_admin(
        self, client, admin_headers, created_problem
    ):
        """Админ видит все проблемы включая rejected."""
        response = client.get(
            f"{ADMIN_URL}/problems",
            headers = admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_filter_by_status(
        self, client, admin_headers, created_problem
    ):
        """Фильтр по статусу."""
        response = client.get(
            f"{ADMIN_URL}/problems",
            params  = {"status": "open"},
            headers = admin_headers,
        )
        assert response.status_code == 200

    def test_regular_user_cannot_list(self, client, auth_headers):
        """Обычный пользователь — 403."""
        response = client.get(
            f"{ADMIN_URL}/problems",
            headers = auth_headers,
        )
        assert response.status_code == 403


class TestRejectProblem:

    def test_moderator_can_reject(
        self, client, moderator_headers, created_problem
    ):
        """Модератор отклоняет проблему."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/reject",
            json    = {"reason": "Нарушение правил"},
            headers = moderator_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"]          == "rejected"
        assert data["resolution_note"] == "Нарушение правил"
        assert data["version"]         == 2

    def test_already_rejected(
        self, client, moderator_headers, created_problem
    ):
        """Повторное отклонение — 400."""
        entity_id = created_problem["entity_id"]

        client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/reject",
            json    = {"reason": "Первое"},
            headers = moderator_headers,
        )
        response = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/reject",
            json    = {"reason": "Второе"},
            headers = moderator_headers,
        )
        assert response.status_code == 400

    def test_regular_user_cannot_reject(
        self, client, auth_headers, created_problem
    ):
        """Обычный пользователь — 403."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/reject",
            json    = {"reason": "Тест"},
            headers = auth_headers,
        )
        assert response.status_code == 403

    def test_reject_not_found(self, client, moderator_headers):
        """Несуществующая проблема — 404."""
        response = client.patch(
            f"{ADMIN_URL}/problems/99999/reject",
            json    = {"reason": "Тест"},
            headers = moderator_headers,
        )
        assert response.status_code == 404


class TestRestoreProblem:

    def test_admin_can_restore(
        self, client, admin_headers, moderator_headers, created_problem
    ):
        """Админ восстанавливает отклонённую проблему."""
        entity_id = created_problem["entity_id"]

        # Отклоняем
        client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/reject",
            json    = {"reason": "Тест"},
            headers = moderator_headers,
        )

        # Восстанавливаем
        response = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/restore",
            headers = admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "open"

    def test_restore_non_rejected(
        self, client, admin_headers, created_problem
    ):
        """Восстановить не-отклонённую — 400."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/restore",
            headers = admin_headers,
        )
        assert response.status_code == 400

    def test_moderator_cannot_restore(
        self, client, moderator_headers, created_problem
    ):
        """Модератор не может восстанавливать — только admin."""
        entity_id = created_problem["entity_id"]
        response  = client.patch(
            f"{ADMIN_URL}/problems/{entity_id}/restore",
            headers = moderator_headers,
        )
        assert response.status_code == 403


# ══════════════════════════════════════════════════════════
# ТЕСТЫ СТАТИСТИКИ
# ══════════════════════════════════════════════════════════

class TestSystemStats:

    def test_admin_can_get_stats(self, client, admin_headers):
        """Админ получает статистику системы."""
        response = client.get(
            f"{ADMIN_URL}/stats",
            headers = admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert "total_users"       in data
        assert "active_users"      in data
        assert "suspended_users"   in data
        assert "total_problems"    in data
        assert "total_votes"       in data
        assert "total_comments"    in data
        assert "cities_covered"    in data

    def test_stats_counts_correctly(
        self, client, admin_headers, registered_user, created_problem
    ):
        """Статистика корректно считает."""
        response = client.get(
            f"{ADMIN_URL}/stats",
            headers = admin_headers,
        )
        data = response.json()
        assert data["total_users"]    >= 1
        assert data["total_problems"] >= 1
        assert data["open_problems"]  >= 1

    def test_moderator_cannot_get_stats(
        self, client, moderator_headers
    ):
        """Модератор не видит системную статистику — только admin."""
        response = client.get(
            f"{ADMIN_URL}/stats",
            headers = moderator_headers,
        )
        assert response.status_code == 403

    def test_regular_user_cannot_get_stats(self, client, auth_headers):
        """Обычный пользователь — 403."""
        response = client.get(
            f"{ADMIN_URL}/stats",
            headers = auth_headers,
        )
        assert response.status_code == 403