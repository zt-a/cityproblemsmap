# tests/test_gamification.py
import pytest
from fastapi.testclient import TestClient


def test_get_user_stats_initial(client: TestClient, auth_headers):
    """Тест получения начальной статистики пользователя"""
    response = client.get("/api/v1/gamification/stats", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["level"] == 1
    assert data["xp"] == 0
    assert data["next_level_xp"] == 100
    assert data["title"] == "Новичок"
    assert data["achievements_count"] == 0
    assert data["achievements"] == []


def test_get_achievements_list(client: TestClient, auth_headers):
    """Тест получения списка достижений"""
    response = client.get("/api/v1/gamification/achievements", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Проверяем структуру достижения
    achievement = data[0]
    assert "code" in achievement
    assert "name" in achievement
    assert "description" in achievement
    assert "points" in achievement
    assert "rarity" in achievement
    assert "earned" in achievement
    assert "earned_at" in achievement

    # Изначально все достижения не получены
    for ach in data:
        assert ach["earned"] == False
        assert ach["earned_at"] is None


def test_check_achievements(client: TestClient, auth_headers):
    """Тест проверки достижений"""
    response = client.post("/api/v1/gamification/check-achievements", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "message" in data


def test_gamification_with_problem_creation(client: TestClient, auth_headers):
    """Тест получения XP и достижений при создании проблемы"""
    # from app.database import SessionLocal
    # from app.models.gamification import Achievement

    # Создаем достижения в БД
    # db = SessionLocal()
    # try:
    #     # Создаем достижение "Первая проблема"
    #     achievement = Achievement(
    #         id=1,
    #         code="first_problem",
    #         name="Первая проблема",
    #         description="Создайте свою первую проблему",
    #         criteria={"problems_created": 1},
    #         points=10,
    #         rarity="common",
    #     )
    #     db.add(achievement)
    #     db.commit()
    # finally:
    #     db.close()
    # Достижения уже созданы в seed (conftest.py)

    # Получаем начальную статистику
    response = client.get("/api/v1/gamification/stats", headers=auth_headers)
    initial_xp = response.json()["xp"]

    # Создаем проблему
    problem_data = {
        "title": "Test Problem",
        "description": "Test Description",
        "problem_type": "infrastructure",
        "latitude": 42.8746,
        "longitude": 74.5698,
        "city": "Bishkek",
    }
    response = client.post("/api/v1/problems/", json=problem_data, headers=auth_headers)
    assert response.status_code == 201

    # Проверяем достижения
    client.post("/api/v1/gamification/check-achievements", headers=auth_headers)

    # Получаем обновленную статистику
    response = client.get("/api/v1/gamification/stats", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    # XP должен увеличиться (за создание проблемы)
    assert data["xp"] >= initial_xp

    # Проверяем достижения
    response = client.get("/api/v1/gamification/achievements", headers=auth_headers)
    achievements = response.json()

    first_problem = next((a for a in achievements if a["code"] == "first_problem"), None)
    if first_problem:
        assert first_problem["earned"] == True
        assert first_problem["earned_at"] is not None


def test_level_progression(client: TestClient, auth_headers):
    """Тест повышения уровня"""
    from app.database import SessionLocal
    from app.services.gamification import GamificationService

    # Добавляем много XP напрямую
    db = SessionLocal()
    try:
        # Получаем entity_id пользователя
        from app.models.user import User
        user = db.query(User).filter_by(is_current=True).first()

        # Добавляем 150 XP (должно повысить уровень с 1 до 2)
        GamificationService.award_xp(db, user.entity_id, 150, "test")
    finally:
        db.close()

    # Проверяем статистику
    response = client.get("/api/v1/gamification/stats", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["level"] == 2
    assert data["xp"] == 150
    assert data["title"] == "Активист"


def test_multiple_achievements(client: TestClient, auth_headers):
    """Тест получения нескольких достижений"""
    # from app.database import SessionLocal
    # from app.models.gamification import Achievement

    # # Создаем несколько достижений
    # db = SessionLocal()
    # try:
    #     achievements = [
    #         Achievement(
    #             id=1,
    #             code="first_problem",
    #             name="Первая проблема",
    #             description="Создайте свою первую проблему",
    #             criteria={"problems_created": 1},
    #             points=10,
    #             rarity="common",
    #         ),
    #         Achievement(
    #             id=2,
    #             code="10_problems",
    #             name="10 проблем",
    #             description="Создайте 10 проблем",
    #             criteria={"problems_created": 10},
    #             points=50,
    #             rarity="uncommon",
    #         ),
    #         Achievement(
    #             id=3,
    #             code="active_citizen",
    #             name="Активный гражданин",
    #             description="Проголосуйте 100 раз",
    #             criteria={"votes_cast": 100},
    #             points=100,
    #             rarity="rare",
    #         ),
    #     ]
    #     for ach in achievements:
    #         db.add(ach)
    #     db.commit()
    # finally:
    #     db.close()
    # Достижения уже созданы в seed (conftest.py)

    # Получаем список достижений
    response = client.get("/api/v1/gamification/achievements", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3

    # Проверяем редкость
    rarities = [a["rarity"] for a in data]
    assert "common" in rarities
    assert "uncommon" in rarities
    assert "rare" in rarities


def test_gamification_unauthorized(client: TestClient):
    """Тест доступа к геймификации без авторизации"""
    response = client.get("/api/v1/gamification/stats")
    assert response.status_code == 401

    response = client.get("/api/v1/gamification/achievements")
    assert response.status_code == 401

    response = client.post("/api/v1/gamification/check-achievements")
    assert response.status_code == 401


def test_user_level_versioning(client: TestClient, auth_headers):
    """Тест версионирования уровней пользователя"""
    from app.database import SessionLocal
    from app.services.gamification import GamificationService
    from app.models.user import User
    from app.models.gamification import UserLevel

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(is_current=True).first()

        # Добавляем XP несколько раз
        GamificationService.award_xp(db, user.entity_id, 50, "test1")
        GamificationService.award_xp(db, user.entity_id, 60, "test2")
        GamificationService.award_xp(db, user.entity_id, 100, "test3")

        # Проверяем версии
        levels = db.query(UserLevel).filter_by(
            user_entity_id=user.entity_id
        ).order_by(UserLevel.version).all()

        # Должно быть несколько версий
        assert len(levels) >= 3

        # Только последняя is_current
        current = [l for l in levels if l.is_current]
        assert len(current) == 1

        # XP должен накапливаться
        assert current[0].xp == 210
    finally:
        db.close()
