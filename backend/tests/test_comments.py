# tests/test_comments.py
import pytest

PROBLEMS_URL = "/api/v1/problems"
REGISTER_URL = "/api/v1/auth/register"

VALID_PROBLEM = {
    "title":        "Сломанный светофор",
    "description":  "Светофор не работает уже неделю",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "traffic_light",
    "nature":       "temporary",
}


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def created_problem(client, auth_headers):
    response = client.post(
        PROBLEMS_URL + "/",
        json=VALID_PROBLEM,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "commenter",
        "email":    "commenter@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    return {"Authorization": f"Bearer {second_user['access_token']}"}


@pytest.fixture
def third_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "commenter2",
        "email":    "commenter2@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def third_headers(third_user):
    return {"Authorization": f"Bearer {third_user['access_token']}"}


def comments_url(problem_entity_id: int) -> str:
    return f"{PROBLEMS_URL}/{problem_entity_id}/comments"


def comment_url(problem_entity_id: int, comment_entity_id: int) -> str:
    return f"{PROBLEMS_URL}/{problem_entity_id}/comments/{comment_entity_id}"


class TestCreateComment:

    def test_create_success(self, client, created_problem, second_headers):
        """Успешное создание комментария."""
        pid      = created_problem["entity_id"]
        response = client.post(
            comments_url(pid),
            json={"content": "Видел этот светофор — действительно не работает"},
            headers=second_headers,
        )
        assert response.status_code == 201
        data = response.json()

        assert data["content"]      == "Видел этот светофор — действительно не работает"
        assert data["comment_type"] == "user"
        assert data["version"]      == 1
        assert data["is_current"]
        assert not data["is_flagged"]

    def test_create_unauthorized(self, client, created_problem):
        """Без токена — 401."""
        pid      = created_problem["entity_id"]
        response = client.post(
            comments_url(pid),
            json={"content": "Комментарий без токена"},
        )
        assert response.status_code == 401

    def test_create_nonexistent_problem(self, client, second_headers):
        """Комментарий к несуществующей проблеме — 404."""
        response = client.post(
            comments_url(99999),
            json={"content": "Комментарий"},
            headers=second_headers,
        )
        assert response.status_code == 404

    def test_create_too_short(self, client, created_problem, second_headers):
        """Слишком короткий комментарий — 422."""
        pid      = created_problem["entity_id"]
        response = client.post(
            comments_url(pid),
            json={"content": "А"},
            headers=second_headers,
        )
        assert response.status_code == 422

    def test_create_increments_comment_count(
        self, client, created_problem, second_headers
    ):
        """После комментария comment_count проблемы увеличивается."""
        pid = created_problem["entity_id"]

        before = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert before["comment_count"] == 0

        client.post(
            comments_url(pid),
            json={"content": "Первый комментарий"},
            headers=second_headers,
        )

        after = client.get(f"{PROBLEMS_URL}/{pid}").json()
        assert after["comment_count"] == 1

    def test_author_can_comment_own_problem(
        self, client, created_problem, auth_headers
    ):
        """Автор может комментировать свою проблему."""
        pid      = created_problem["entity_id"]
        response = client.post(
            comments_url(pid),
            json={"content": "Обновление от автора — яму стало больше"},
            headers=auth_headers,
        )
        assert response.status_code == 201


class TestReplyComment:

    def test_reply_success(
        self, client, created_problem, auth_headers, second_headers
    ):
        """Успешный ответ на корневой комментарий."""
        pid = created_problem["entity_id"]

        # Создаём корневой комментарий
        root = client.post(
            comments_url(pid),
            json={"content": "Корневой комментарий"},
            headers=second_headers,
        ).json()

        # Отвечаем на него
        response = client.post(
            comments_url(pid),
            json={
                "content":          "Ответ на комментарий",
                "parent_entity_id": root["entity_id"],
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent_entity_id"] == root["entity_id"]
        assert data["content"]          == "Ответ на комментарий"

    def test_reply_to_reply_forbidden(
        self, client, created_problem, auth_headers, second_headers, third_headers
    ):
        """
        Нельзя отвечать на ответ — только на корневой комментарий.
        Защита от глубокой вложенности.
        """
        pid = created_problem["entity_id"]

        # Корневой
        root = client.post(
            comments_url(pid),
            json={"content": "Корневой"},
            headers=second_headers,
        ).json()

        # Ответ на корневой
        reply = client.post(
            comments_url(pid),
            json={
                "content":          "Ответ первого уровня",
                "parent_entity_id": root["entity_id"],
            },
            headers=auth_headers,
        ).json()

        # Попытка ответить на ответ — 400
        response = client.post(
            comments_url(pid),
            json={
                "content":          "Ответ второго уровня",
                "parent_entity_id": reply["entity_id"],
            },
            headers=third_headers,
        )
        assert response.status_code == 400

    def test_reply_nonexistent_parent(
        self, client, created_problem, second_headers
    ):
        """Ответ на несуществующий комментарий — 404."""
        pid      = created_problem["entity_id"]
        response = client.post(
            comments_url(pid),
            json={
                "content":          "Ответ",
                "parent_entity_id": 99999,
            },
            headers=second_headers,
        )
        assert response.status_code == 404


class TestGetComments:

    def test_get_empty(self, client, created_problem):
        """Пустое дерево если комментариев нет."""
        pid      = created_problem["entity_id"]
        response = client.get(comments_url(pid))

        assert response.status_code == 200
        assert response.json()      == []

    def test_get_tree_structure(
        self, client, created_problem, auth_headers, second_headers
    ):
        """
        Комментарии возвращаются в виде дерева.
        Корневой содержит replies со вложенными ответами.
        """
        pid = created_problem["entity_id"]

        # Корневой комментарий
        root = client.post(
            comments_url(pid),
            json={"content": "Корневой комментарий"},
            headers=second_headers,
        ).json()

        # Два ответа на корневой
        client.post(
            comments_url(pid),
            json={
                "content":          "Первый ответ",
                "parent_entity_id": root["entity_id"],
            },
            headers=auth_headers,
        )
        client.post(
            comments_url(pid),
            json={
                "content":          "Второй ответ",
                "parent_entity_id": root["entity_id"],
            },
            headers=auth_headers,
        )

        response = client.get(comments_url(pid))
        tree     = response.json()

        # Один корневой
        assert len(tree)           == 1
        assert tree[0]["content"]  == "Корневой комментарий"

        # Два вложенных ответа
        assert len(tree[0]["replies"]) == 2

    def test_get_nonexistent_problem(self, client):
        """Комментарии несуществующей проблемы — 404."""
        response = client.get(comments_url(99999))
        assert response.status_code == 404

    def test_get_unauthorized_allowed(self, client, created_problem):
        """Просмотр комментариев доступен без авторизации."""
        pid      = created_problem["entity_id"]
        response = client.get(comments_url(pid))
        assert response.status_code == 200


class TestEditComment:

    def test_edit_success(
        self, client, created_problem, second_headers
    ):
        """
        Редактирование создаёт новую версию.
        Оригинальный текст сохраняется в истории.
        """
        pid = created_problem["entity_id"]

        comment = client.post(
            comments_url(pid),
            json={"content": "Оригинальный текст"},
            headers=second_headers,
        ).json()

        response = client.patch(
            comment_url(pid, comment["entity_id"]),
            json={"content": "Исправленный текст"},
            headers=second_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Исправленный текст"
        assert data["version"] == 2

    def test_edit_another_users_comment_forbidden(
        self, client, created_problem, second_headers, auth_headers
    ):
        """Нельзя редактировать чужой комментарий — 403."""
        pid = created_problem["entity_id"]

        comment = client.post(
            comments_url(pid),
            json={"content": "Чужой комментарий"},
            headers=second_headers,
        ).json()

        response = client.patch(
            comment_url(pid, comment["entity_id"]),
            json={"content": "Попытка изменить чужой"},
            headers=auth_headers,  # другой пользователь
        )
        assert response.status_code == 403

    def test_edit_unauthorized(self, client, created_problem, second_headers):
        """Без токена — 401."""
        pid = created_problem["entity_id"]

        comment = client.post(
            comments_url(pid),
            json={"content": "Комментарий"},
            headers=second_headers,
        ).json()

        response = client.patch(
            comment_url(pid, comment["entity_id"]),
            json={"content": "Попытка без токена"},
        )
        assert response.status_code == 401

    def test_edit_nonexistent_comment(
        self, client, created_problem, second_headers
    ):
        """Редактирование несуществующего комментария — 404."""
        pid      = created_problem["entity_id"]
        response = client.patch(
            comment_url(pid, 99999),
            json={"content": "Текст"},
            headers=second_headers,
        )
        assert response.status_code == 404


class TestFlagComment:

    def test_flag_by_user(
        self, client, created_problem, auth_headers, second_headers
    ):
        """
        Обычный пользователь может пожаловаться на комментарий.
        is_flagged становится True, comment_type остаётся 'user'.
        """
        pid = created_problem["entity_id"]

        comment = client.post(
            comments_url(pid),
            json={"content": "Подозрительный комментарий"},
            headers=second_headers,
        ).json()

        response = client.patch(
            comment_url(pid, comment["entity_id"]) + "/flag",
            params={"reason": "Спам"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_flagged"]
        assert data["comment_type"] == "user"  # тип не меняется

    def test_flag_nonexistent_comment(
        self, client, created_problem, auth_headers
    ):
        """Жалоба на несуществующий комментарий — 404."""
        pid      = created_problem["entity_id"]
        response = client.patch(
            comment_url(pid, 99999) + "/flag",
            params={"reason": "Спам"},
            headers=auth_headers,
        )
        assert response.status_code == 404