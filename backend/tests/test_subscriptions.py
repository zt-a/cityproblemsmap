# tests/test_subscriptions.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.models.zone import Zone
from app.models.subscription import Subscription
from app.services.auth import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """Создать тестового пользователя"""
    entity_id = User.next_entity_id(db)
    user = User(
        entity_id=entity_id,
        version=1,
        is_current=True,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        country="Kyrgyzstan",
        city="Bishkek",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Заголовки авторизации"""
    token = create_access_token(test_user.entity_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_problem(db: Session, test_user):
    """Создать тестовую проблему"""
    from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

    entity_id = Problem.next_entity_id(db)
    problem = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        author_entity_id=test_user.entity_id,
        title="Test Problem",
        description="Test Description",
        country="Kyrgyzstan",
        city="Bishkek",
        location=ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326),
        problem_type="infrastructure",
        nature="permanent",
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@pytest.fixture
def test_zone(db: Session):
    """Создать тестовую зону"""
    entity_id = Zone.next_entity_id(db)
    zone = Zone(
        entity_id=entity_id,
        version=1,
        is_current=True,
        name="Test District",
        zone_type="district",
        country="Kyrgyzstan",
        city="Bishkek",
        center_lat=42.8746,
        center_lon=74.5698,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


class TestSubscribeToProblem:
    """Тесты подписки на проблему"""

    def test_subscribe_to_problem_success(self, client, db, test_problem, auth_headers):
        """Успешная подписка на проблему"""
        response = client.post(
            f"/api/v1/subscriptions/problems/{test_problem.entity_id}",
            json={"notification_types": ["email"]},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "problem"
        assert data["target_entity_id"] == test_problem.entity_id
        assert data["notification_types"] == ["email"]

    def test_subscribe_to_problem_duplicate(self, client, db, test_problem, test_user, auth_headers):
        """Повторная подписка должна вернуть ошибку"""
        # Создаем подписку
        entity_id = Subscription.next_entity_id(db)
        subscription = Subscription(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            notification_types=["email"],
        )
        db.add(subscription)
        db.commit()

        # Пытаемся подписаться снова
        response = client.post(
            f"/api/v1/subscriptions/problems/{test_problem.entity_id}",
            json={"notification_types": ["email"]},
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert "уже существует" in response.json()["detail"]

    def test_subscribe_to_nonexistent_problem(self, client, auth_headers):
        """Подписка на несуществующую проблему"""
        response = client.post(
            "/api/v1/subscriptions/problems/99999",
            json={"notification_types": ["email"]},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_subscribe_without_auth(self, client, test_problem):
        """Подписка без авторизации"""
        response = client.post(
            f"/api/v1/subscriptions/problems/{test_problem.entity_id}",
            json={"notification_types": ["email"]},
        )

        assert response.status_code == 401


class TestUnsubscribeFromProblem:
    """Тесты отписки от проблемы"""

    def test_unsubscribe_from_problem_success(self, client, db, test_problem, test_user, auth_headers):
        """Успешная отписка от проблемы"""
        # Создаем подписку
        entity_id = Subscription.next_entity_id(db)
        subscription = Subscription(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            notification_types=["email"],
        )
        db.add(subscription)
        db.commit()

        # Отписываемся
        response = client.delete(
            f"/api/v1/subscriptions/problems/{test_problem.entity_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Проверяем что подписка помечена как неактуальная
        db.refresh(subscription)
        assert subscription.is_current is False

    def test_unsubscribe_nonexistent(self, client, test_problem, auth_headers):
        """Отписка от несуществующей подписки"""
        response = client.delete(
            f"/api/v1/subscriptions/problems/{test_problem.entity_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSubscribeToZone:
    """Тесты подписки на зону"""

    def test_subscribe_to_zone_success(self, client, db, test_zone, auth_headers):
        """Успешная подписка на зону"""
        response = client.post(
            f"/api/v1/subscriptions/zones/{test_zone.entity_id}",
            json={"notification_types": ["email", "push"]},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "zone"
        assert data["target_entity_id"] == test_zone.entity_id
        assert set(data["notification_types"]) == {"email", "push"}

    def test_subscribe_to_nonexistent_zone(self, client, auth_headers):
        """Подписка на несуществующую зону"""
        response = client.post(
            "/api/v1/subscriptions/zones/99999",
            json={"notification_types": ["email"]},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGetMySubscriptions:
    """Тесты получения подписок"""

    def test_get_all_subscriptions(self, client, db, test_problem, test_zone, test_user, auth_headers):
        """Получить все подписки пользователя"""
        # Создаем подписки
        for target_type, target_id in [("problem", test_problem.entity_id), ("zone", test_zone.entity_id)]:
            entity_id = Subscription.next_entity_id(db)
            subscription = Subscription(
                entity_id=entity_id,
                version=1,
                is_current=True,
                user_entity_id=test_user.entity_id,
                target_type=target_type,
                target_entity_id=target_id,
                notification_types=["email"],
            )
            db.add(subscription)
        db.commit()

        response = client.get("/api/v1/subscriptions/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_subscriptions_filtered(self, client, db, test_problem, test_zone, test_user, auth_headers):
        """Получить подписки с фильтром по типу"""
        # Создаем подписки
        for target_type, target_id in [("problem", test_problem.entity_id), ("zone", test_zone.entity_id)]:
            entity_id = Subscription.next_entity_id(db)
            subscription = Subscription(
                entity_id=entity_id,
                version=1,
                is_current=True,
                user_entity_id=test_user.entity_id,
                target_type=target_type,
                target_entity_id=target_id,
                notification_types=["email"],
            )
            db.add(subscription)
        db.commit()

        response = client.get(
            "/api/v1/subscriptions/?target_type=problem",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["target_type"] == "problem"


class TestUpdateSubscription:
    """Тесты обновления подписки"""

    def test_update_notification_types(self, client, db, test_problem, test_user, auth_headers):
        """Обновить типы уведомлений"""
        # Создаем подписку
        entity_id = Subscription.next_entity_id(db)
        subscription = Subscription(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            notification_types=["email"],
        )
        db.add(subscription)
        db.commit()

        # Обновляем
        response = client.patch(
            f"/api/v1/subscriptions/{entity_id}",
            json={"notification_types": ["email", "push"]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["notification_types"]) == {"email", "push"}
        assert data["version"] == 2

    def test_update_nonexistent_subscription(self, client, auth_headers):
        """Обновление несуществующей подписки"""
        response = client.patch(
            "/api/v1/subscriptions/99999",
            json={"notification_types": ["email"]},
            headers=auth_headers,
        )

        assert response.status_code == 404
