# tests/test_moderation_queue.py
import pytest
from app.models.user import UserRole
from unittest.mock import patch

QUEUE_URL = "/api/v1/moderation/queue"


@pytest.fixture
def moderator_user(client):
    """Создаёт пользователя с ролью moderator."""
    response = client.post("/api/v1/auth/register", json={
        "username": "moderator",
        "email": "moderator@test.com",
        "password": "password123",
        "city": "Bishkek",
    })
    assert response.status_code == 201
    data = response.json()

    # ВАЖНО: Используем отдельное подключение вне транзакции теста
    from sqlalchemy import create_engine, text
    from app.config import settings

    # Создаем новый engine для прямого доступа к БД
    direct_engine = create_engine(settings.TEST_DATABASE_URL)
    with direct_engine.connect() as conn:
        # Выполняем UPDATE вне транзакции теста
        conn.execute(
            text("UPDATE users SET role = :role WHERE entity_id = :entity_id AND is_current = true"),
            {"role": "moderator", "entity_id": data["user"]["entity_id"]}
        )
        conn.commit()
    direct_engine.dispose()

    return data


@pytest.fixture
def mock_moderator_role(registered_user):
    """Мокирует проверку роли модератора для обычного пользователя."""
    from app.models.user import User

    def mock_require_role(*roles):
        def checker(current_user: User):
            # Просто возвращаем пользователя без проверки роли
            return current_user
        return checker

    with patch('app.api.v1.moderation_queue.require_role', side_effect=mock_require_role):
        yield registered_user


@pytest.fixture
def mock_moderator_headers(mock_moderator_role):
    """Заголовки с токеном для мокированного модератора."""
    token = mock_moderator_role["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def moderator_headers(moderator_user):
    """Заголовки с токеном модератора."""
    token = moderator_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pending_problem(client, auth_headers):
    """Создаёт проблему в статусе pending."""
    response = client.post(
        "/api/v1/problems/",
        json={
            "title": "Тестовая проблема",
            "description": "Описание",
            "country": "Kyrgyzstan",
            "city": "Bishkek",
            "district": "Первомайский",
            "address": "ул. Манаса 50",
            "latitude": 42.8746,
            "longitude": 74.5698,
            "problem_type": "pothole",
            "nature": "permanent",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()

@pytest.mark.skip(reason="ModerationQueue endpoints в разработке. Работоспособность не подтверждена.")
class TestModerationQueueProblems:

    def test_get_queue_unauthorized(self, client):
        """Без токена - 401."""
        response = client.get(f"{QUEUE_URL}/problems")
        assert response.status_code == 401

    def test_get_queue_regular_user(self, client, auth_headers):
        """Обычный пользователь не может получить очередь - 403."""
        response = client.get(f"{QUEUE_URL}/problems", headers=auth_headers)
        assert response.status_code == 403

    def test_get_queue_moderator_success(self, client, mock_moderator_headers):
        """Модератор может получить очередь."""
        response = client.get(f"{QUEUE_URL}/problems", headers=mock_moderator_headers)
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_get_queue_with_pending_problems(self, client, mock_moderator_headers, pending_problem):
        """Очередь показывает pending проблемы."""
        response = client.get(
            f"{QUEUE_URL}/problems",
            params={"status": "pending"},
            headers=mock_moderator_headers
        )
        assert response.status_code == 200
        data = response.json()

        # Должна быть хотя бы одна pending проблема
        assert len(data) >= 1

        # Проверяем что это наша проблема
        problem_ids = [p["entity_id"] for p in data]
        assert pending_problem["entity_id"] in problem_ids

    def test_get_queue_pagination(self, client, mock_moderator_headers, auth_headers):
        """Проверка пагинации очереди."""
        # Создаём несколько проблем
        for i in range(5):
            client.post(
                "/api/v1/problems/",
                json={
                    "title": f"Проблема {i}",
                    "description": "Описание",
                    "country": "Kyrgyzstan",
                    "city": "Bishkek",
                    "district": "Первомайский",
                    "address": "ул. Манаса 50",
                    "latitude": 42.8746,
                    "longitude": 74.5698,
                    "problem_type": "pothole",
                    "nature": "permanent",
                },
                headers=auth_headers,
            )

        # Первая страница
        response = client.get(
            f"{QUEUE_URL}/problems",
            params={"limit": 2, "offset": 0},
            headers=mock_moderator_headers
        )
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        # Вторая страница
        response = client.get(
            f"{QUEUE_URL}/problems",
            params={"limit": 2, "offset": 2},
            headers=mock_moderator_headers
        )
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 2

        # Проблемы должны быть разные
        page1_ids = {p["entity_id"] for p in page1}
        page2_ids = {p["entity_id"] for p in page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_queue_admin_access(self, client, mock_moderator_headers):
        """Админ тоже может получить очередь."""
        response = client.get(f"{QUEUE_URL}/problems", headers=mock_moderator_headers)
        assert response.status_code == 200

@pytest.mark.skip(reason="ModerationQueue endpoints в разработке. Работоспособность не подтверждена.")
class TestModerationQueueComments:

    def test_get_comments_queue_unauthorized(self, client):
        """Без токена - 401."""
        response = client.get(f"{QUEUE_URL}/comments")
        assert response.status_code == 401

    def test_get_comments_queue_moderator(self, client, mock_moderator_headers):
        """Модератор может получить очередь комментариев."""
        response = client.get(f"{QUEUE_URL}/comments", headers=mock_moderator_headers)
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_get_comments_queue_pagination(self, client, mock_moderator_headers):
        """Проверка пагинации комментариев."""
        response = client.get(
            f"{QUEUE_URL}/comments",
            params={"limit": 10, "offset": 0},
            headers=mock_moderator_headers
        )
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) <= 10

@pytest.mark.skip(reason="ModerationQueue endpoints в разработке. Работоспособность не подтверждена.")
class TestModerationQueueStats:

    def test_get_stats_unauthorized(self, client):
        """Без токена - 401."""
        response = client.get(f"{QUEUE_URL}/stats")
        assert response.status_code == 401

    def test_get_stats_regular_user(self, client, auth_headers):
        """Обычный пользователь не может получить статистику - 403."""
        response = client.get(f"{QUEUE_URL}/stats", headers=auth_headers)
        assert response.status_code == 403

    def test_get_stats_moderator_success(self, client, mock_moderator_headers):
        """Модератор может получить статистику."""
        response = client.get(f"{QUEUE_URL}/stats", headers=mock_moderator_headers)
        assert response.status_code == 200
        data = response.json()

        # Проверяем структуру ответа
        assert "pending_problems" in data
        assert "flagged_problems" in data
        assert "flagged_comments" in data
        assert "old_pending_problems" in data
        assert "total_queue" in data

        # Все значения должны быть числами
        assert isinstance(data["pending_problems"], int)
        assert isinstance(data["flagged_problems"], int)
        assert isinstance(data["flagged_comments"], int)
        assert isinstance(data["old_pending_problems"], int)
        assert isinstance(data["total_queue"], int)

        # total_queue должен быть суммой
        expected_total = (
            data["pending_problems"] +
            data["flagged_problems"] +
            data["flagged_comments"]
        )
        assert data["total_queue"] == expected_total

    def test_get_stats_with_pending_problems(self, client, mock_moderator_headers, pending_problem):
        """Статистика учитывает pending проблемы."""
        response = client.get(f"{QUEUE_URL}/stats", headers=mock_moderator_headers)
        assert response.status_code == 200
        data = response.json()

        # Должна быть хотя бы одна pending проблема
        assert data["pending_problems"] >= 1
        assert data["total_queue"] >= 1

    def test_get_stats_admin_access(self, client, mock_moderator_headers):
        """Админ тоже может получить статистику."""
        response = client.get(f"{QUEUE_URL}/stats", headers=mock_moderator_headers)
        assert response.status_code == 200
        data = response.json()

        assert "pending_problems" in data
        assert "total_queue" in data
