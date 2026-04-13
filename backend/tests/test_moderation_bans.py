# tests/test_moderation_bans.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.main import app
from app.models.user import User, UserRole
from app.services.auth import create_access_token, hash_password


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(db: Session):
    entity_id = User.next_entity_id(db)
    user = User(
        entity_id=entity_id,
        version=1,
        is_current=True,
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password"),
        country="Kyrgyzstan",
        city="Bishkek",
        role=UserRole.user,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def moderator_user(db: Session):
    entity_id = User.next_entity_id(db)
    user = User(
        entity_id=entity_id,
        version=1,
        is_current=True,
        username="moderator",
        email="moderator@example.com",
        hashed_password=hash_password("password"),
        country="Kyrgyzstan",
        city="Bishkek",
        role=UserRole.moderator,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session):
    entity_id = User.next_entity_id(db)
    user = User(
        entity_id=entity_id,
        version=1,
        is_current=True,
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("password"),
        country="Kyrgyzstan",
        city="Bishkek",
        role=UserRole.admin,
        is_banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(test_user.entity_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def moderator_headers(moderator_user):
    token = create_access_token(moderator_user.entity_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(admin_user.entity_id)
    return {"Authorization": f"Bearer {token}"}


class TestBanUser:
    """Тесты блокировки пользователей"""

    def test_ban_user_permanent(self, client, db, test_user, moderator_headers):
        """Постоянная блокировка пользователя"""
        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban",
            json={
                "reason": "Спам и нарушение правил",
                "duration_days": None,
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_banned"] is True
        assert data["ban_reason"] == "Спам и нарушение правил"
        assert data["ban_until"] is None  # Постоянный бан

    def test_ban_user_temporary(self, client, db, test_user, moderator_headers):
        """Временная блокировка на 7 дней"""
        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban",
            json={
                "reason": "Временное нарушение",
                "duration_days": 7,
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_banned"] is True
        assert data["ban_until"] is not None

    def test_ban_self(self, client, moderator_user, moderator_headers):
        """Нельзя забанить самого себя"""
        response = client.post(
            f"/api/v1/moderation/users/{moderator_user.entity_id}/ban",
            json={"reason": "Test"},
            headers=moderator_headers,
        )

        assert response.status_code == 400
        assert "самого себя" in response.json()["detail"]

    def test_ban_admin_by_moderator(self, client, admin_user, moderator_headers):
        """Модератор не может забанить админа"""
        response = client.post(
            f"/api/v1/moderation/users/{admin_user.entity_id}/ban",
            json={"reason": "Test"},
            headers=moderator_headers,
        )

        assert response.status_code == 403

    def test_ban_already_banned(self, client, db, test_user, moderator_user, moderator_headers):
        """Нельзя забанить уже забаненного"""
        # Баним пользователя
        from app.services.versioning import create_new_version
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Already banned",
        )

        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban",
            json={"reason": "Test"},
            headers=moderator_headers,
        )

        assert response.status_code == 409

    def test_ban_unauthorized(self, client, test_user, auth_headers):
        """Обычный пользователь не может банить"""
        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban",
            json={"reason": "Test"},
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestUnbanUser:
    """Тесты разблокировки пользователей"""

    def test_unban_user_success(self, client, db, test_user, moderator_user, moderator_headers):
        """Успешная разблокировка"""
        # Сначала баним
        from app.services.versioning import create_new_version
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Test ban",
            banned_at=datetime.now(timezone.utc),
        )

        # Разбаниваем
        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/unban",
            json={"reason": "Апелляция принята"},
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_banned"] is False
        assert data["ban_reason"] is None

    def test_unban_not_banned(self, client, test_user, moderator_headers):
        """Нельзя разбанить незабаненного"""
        response = client.post(
            f"/api/v1/moderation/users/{test_user.entity_id}/unban",
            json={"reason": "Test"},
            headers=moderator_headers,
        )

        assert response.status_code == 400


class TestGetBanInfo:
    """Тесты получения информации о бане"""

    def test_get_ban_info_banned(self, client, db, test_user, moderator_user, moderator_headers):
        """Информация о забаненном пользователе"""
        from app.services.versioning import create_new_version
        ban_time = datetime.now(timezone.utc)
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Test reason",
            banned_at=ban_time,
        )

        response = client.get(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban-info",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_banned"] is True
        assert data["ban_reason"] == "Test reason"

    def test_get_ban_info_not_banned(self, client, test_user, moderator_headers):
        """Информация о незабаненном пользователе"""
        response = client.get(
            f"/api/v1/moderation/users/{test_user.entity_id}/ban-info",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_banned"] is False


class TestGetBannedUsers:
    """Тесты получения списка забаненных"""

    def test_get_banned_users_list(self, client, db, test_user, moderator_user, moderator_headers):
        """Получить список забаненных пользователей"""
        # Баним пользователя
        from app.services.versioning import create_new_version
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Test",
            banned_at=datetime.now(timezone.utc),
        )

        response = client.get(
            "/api/v1/moderation/banned-users",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(item["entity_id"] == test_user.entity_id for item in data["items"])


class TestCheckExpiredBans:
    """Тесты проверки истекших банов"""

    def test_check_expired_bans(self, client, db, test_user, moderator_user, admin_headers):
        """Автоматическая разблокировка истекших банов"""
        # Баним с истекшим сроком
        from app.services.versioning import create_new_version
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Temporary",
            ban_until=expired_time,
            banned_at=datetime.now(timezone.utc) - timedelta(days=8),
        )

        response = client.post(
            "/api/v1/moderation/check-expired-bans",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["unbanned_count"] >= 1

    def test_check_expired_bans_unauthorized(self, client, moderator_headers):
        """Только админ может проверять истекшие баны"""
        response = client.post(
            "/api/v1/moderation/check-expired-bans",
            headers=moderator_headers,
        )

        assert response.status_code == 403


class TestBannedUserAccess:
    """Тесты доступа забаненных пользователей"""

    def test_banned_user_cannot_access_api(self, client, db, test_user, moderator_user):
        """Забаненный пользователь не может использовать API"""
        # Баним пользователя
        from app.services.versioning import create_new_version
        create_new_version(
            db=db,
            model_class=User,
            entity_id=test_user.entity_id,
            changed_by_id=moderator_user.entity_id,
            change_reason="test_ban",
            is_banned=True,
            ban_reason="Banned for testing",
        )

        # Пытаемся получить доступ
        token = create_access_token(test_user.entity_id)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 403
        assert "заблокирован" in response.json()["detail"].lower()
