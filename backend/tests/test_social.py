# tests/test_social.py
import pytest
from fastapi.testclient import TestClient


def test_get_user_profile(client: TestClient, auth_headers, registered_user):
    """Тест получения профиля пользователя"""
    user_id = registered_user["user"]["entity_id"]

    response = client.get(f"/api/v1/social/profile/{user_id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["user_entity_id"] == user_id
    assert data["username"] == "testuser"
    assert data["reputation"] >= 0
    assert data["followers_count"] == 0
    assert data["following_count"] == 0
    assert data["problems_count"] == 0


def test_get_nonexistent_user_profile(client: TestClient, auth_headers):
    """Тест получения профиля несуществующего пользователя"""
    response = client.get("/api/v1/social/profile/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_my_profile(client: TestClient, auth_headers):
    """Тест обновления своего профиля"""
    update_data = {
        "bio": "Test bio",
        "website": "https://example.com",
        "social_links": {
            "twitter": "https://twitter.com/testuser",
            "github": "https://github.com/testuser",
        },
    }

    response = client.patch("/api/v1/social/profile", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["bio"] == "Test bio"
    assert data["website"] == "https://example.com"
    assert data["social_links"]["twitter"] == "https://twitter.com/testuser"
    assert data["social_links"]["github"] == "https://github.com/testuser"


def test_update_profile_with_avatar(client: TestClient, auth_headers):
    """Тест обновления профиля с аватаром"""
    update_data = {
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "New bio",
    }

    response = client.patch("/api/v1/social/profile", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["avatar_url"] == "https://example.com/avatar.jpg"
    assert data["bio"] == "New bio"


def test_follow_user(client: TestClient, auth_headers):
    """Тест подписки на пользователя"""
    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    assert response.status_code == 201
    user2_id = response.json()["user"]["entity_id"]

    # Подписываемся на второго пользователя
    response = client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully followed"

    # Проверяем что подписка создалась
    response = client.get(f"/api/v1/social/profile/{user2_id}", headers=auth_headers)
    data = response.json()
    assert data["followers_count"] == 1


def test_follow_yourself(client: TestClient, auth_headers, registered_user):
    """Тест попытки подписаться на себя"""
    user_id = registered_user["user"]["entity_id"]

    response = client.post(f"/api/v1/social/follow/{user_id}", headers=auth_headers)
    assert response.status_code == 400
    assert "Cannot follow yourself" in response.json()["detail"]


def test_follow_nonexistent_user(client: TestClient, auth_headers):
    """Тест подписки на несуществующего пользователя"""
    response = client.post("/api/v1/social/follow/99999", headers=auth_headers)
    assert response.status_code == 404


def test_follow_already_following(client: TestClient, auth_headers):
    """Тест повторной подписки на пользователя"""
    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    user2_id = response.json()["user"]["entity_id"]

    # Подписываемся первый раз
    response = client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)
    assert response.status_code == 200

    # Пытаемся подписаться второй раз
    response = client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)
    assert response.status_code == 400
    assert "Already following" in response.json()["detail"]


def test_unfollow_user(client: TestClient, auth_headers):
    """Тест отписки от пользователя"""
    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    user2_id = response.json()["user"]["entity_id"]

    # Подписываемся
    client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)

    # Отписываемся
    response = client.delete(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully unfollowed"

    # Проверяем что подписка удалилась
    response = client.get(f"/api/v1/social/profile/{user2_id}", headers=auth_headers)
    data = response.json()
    assert data["followers_count"] == 0


def test_unfollow_not_following(client: TestClient, auth_headers):
    """Тест отписки от пользователя, на которого не подписан"""
    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    user2_id = response.json()["user"]["entity_id"]

    # Пытаемся отписаться без подписки
    response = client.delete(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_activity_feed_empty(client: TestClient, auth_headers):
    """Тест получения пустой ленты активности"""
    response = client.get("/api/v1/social/feed", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["activities"] == []
    assert data["total"] == 0


def test_get_activity_feed_with_activities(client: TestClient, auth_headers):
    """Тест получения ленты активности с событиями"""
    from app.database import SessionLocal
    from app.models.activity import Activity
    from app.models.user import User

    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    user2_id = response.json()["user"]["entity_id"]

    # Подписываемся на второго пользователя
    client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)

    # Создаем активность для второго пользователя
    db = SessionLocal()
    try:
        activity = Activity(
            entity_id=Activity.next_entity_id(db),
            version=1,
            is_current=True,
            user_entity_id=user2_id,
            action_type="problem_created",
            target_type="problem",
            target_entity_id=1,
            description="Created a new problem",
            changed_by_id=user2_id,
        )
        db.add(activity)
        db.commit()
    finally:
        db.close()

    # Получаем ленту
    response = client.get("/api/v1/social/feed", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data["activities"]) == 1
    assert data["total"] == 1
    assert data["activities"][0]["user_id"] == user2_id
    assert data["activities"][0]["action_type"] == "problem_created"


def test_activity_feed_pagination(client: TestClient, auth_headers):
    """Тест пагинации ленты активности"""
    response = client.get("/api/v1/social/feed?limit=10&offset=0", headers=auth_headers)
    assert response.status_code == 200

def test_profile_versioning(client: TestClient, auth_headers):
    """Тест версионирования профиля"""
    from app.database import SessionLocal
    from app.models.social import UserProfile
    from app.models.user import User

    # Обновляем профиль несколько раз
    client.patch("/api/v1/social/profile", json={"bio": "Bio 1"}, headers=auth_headers)
    client.patch("/api/v1/social/profile", json={"bio": "Bio 2"}, headers=auth_headers)
    client.patch("/api/v1/social/profile", json={"bio": "Bio 3"}, headers=auth_headers)

    # Проверяем версии
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(is_current=True).first()
        profiles = db.query(UserProfile).filter_by(
            user_entity_id=user.entity_id
        ).all()
        # Должно быть минимум 3 версии
        assert len(profiles) >= 3
        # Только последняя is_current
        current = [p for p in profiles if p.is_current]
        assert len(current) == 1
        assert current[0].bio == "Bio 3"
        # Проверяем что версии возрастают
        versions = sorted(profiles, key=lambda x: x.version)
        assert versions[-1].version >= 3
    finally:
        db.close()

def test_follow_soft_delete(client: TestClient, auth_headers):
    """Тест мягкого удаления подписки"""
    from app.database import SessionLocal
    from app.models.social import Follow

    # Создаем второго пользователя
    user2_data = {
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123",
        "city": "Bishkek",
    }
    response = client.post("/api/v1/auth/register", json=user2_data)
    user2_id = response.json()["user"]["entity_id"]

    # Подписываемся
    client.post(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)

    # Отписываемся
    client.delete(f"/api/v1/social/follow/{user2_id}", headers=auth_headers)

    # Проверяем что запись не удалена, а помечена is_current=False
    db = SessionLocal()
    try:
        follows = db.query(Follow).filter_by(
            follower_entity_id=1,
            following_entity_id=user2_id,
        ).all()

        assert len(follows) == 1
        assert follows[0].is_current == False
        assert follows[0].superseded_at is not None
    finally:
        db.close()


def test_social_unauthorized(client: TestClient):
    """Тест доступа к социальным функциям без авторизации"""
    response = client.get("/api/v1/social/profile/1")
    assert response.status_code in (200, 404)  # публичный эндпоинт

    response = client.patch("/api/v1/social/profile", json={"bio": "test"})
    assert response.status_code == 401

    response = client.post("/api/v1/social/follow/2")
    assert response.status_code == 401

    response = client.delete("/api/v1/social/follow/2")
    assert response.status_code == 401

    response = client.get("/api/v1/social/feed")
    assert response.status_code == 401
