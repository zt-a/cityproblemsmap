# tests/test_ai_duplicates.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from app.main import app
from app.models.user import User
from app.models.problem import Problem
from app.services.auth import create_access_token, hash_password
from app.services.ai_duplicates import DuplicateDetector


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
def test_problems(db: Session, test_user):
    """Создать набор тестовых проблем"""
    problems = []

    # Проблема 1: Яма на дороге
    entity_id = Problem.next_entity_id(db)
    p1 = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        author_entity_id=test_user.entity_id,
        title="Большая яма на дороге",
        description="На улице Ленина большая яма, нужен ремонт",
        city="Bishkek",
        country="Kyrgyzstan",
        location=ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326),
        problem_type="infrastructure",
        nature="permanent",
    )
    db.add(p1)
    problems.append(p1)

    # Проблема 2: Похожая яма (дубликат)
    entity_id = Problem.next_entity_id(db)
    p2 = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        author_entity_id=test_user.entity_id,
        title="Яма на улице Ленина",
        description="Огромная яма на дороге, требуется срочный ремонт",
        city="Bishkek",
        country="Kyrgyzstan",
        location=ST_SetSRID(ST_MakePoint(74.5700, 42.8748), 4326),  # Рядом
        problem_type="infrastructure",
        nature="permanent",
    )
    db.add(p2)
    problems.append(p2)

    # Проблема 3: Совсем другая проблема
    entity_id = Problem.next_entity_id(db)
    p3 = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        author_entity_id=test_user.entity_id,
        title="Мусор в парке",
        description="В парке Панфилова много мусора",
        city="Bishkek",
        country="Kyrgyzstan",
        location=ST_SetSRID(ST_MakePoint(74.6000, 42.8800), 4326),  # Далеко
        problem_type="other",
        nature="permanent",
    )
    db.add(p3)
    problems.append(p3)

    db.commit()
    for p in problems:
        db.refresh(p)

    return problems


class TestDuplicateDetector:
    """Тесты сервиса определения дубликатов"""

    def test_find_text_duplicates(self, db, test_problems):
        """Поиск текстовых дубликатов"""
        detector = DuplicateDetector(similarity_threshold=0.5)
        problem = test_problems[0]  # Первая яма

        duplicates = detector.find_duplicates(db, problem, city="Bishkek", limit=10)

        # Должна найтись вторая яма как дубликат
        assert len(duplicates) > 0
        duplicate_ids = [p.entity_id for p, _ in duplicates]
        assert test_problems[1].entity_id in duplicate_ids
        # Мусор в парке не должен быть в дубликатах
        assert test_problems[2].entity_id not in duplicate_ids

    def test_find_location_duplicates(self, db, test_problems):
        """Поиск дубликатов по геолокации"""
        detector = DuplicateDetector()
        problem = test_problems[0]

        duplicates = detector.find_similar_by_location(
            db, problem, radius_meters=500, limit=10
        )

        # Вторая яма рядом, должна найтись
        assert len(duplicates) > 0
        duplicate_ids = [p.entity_id for p, _ in duplicates]
        assert test_problems[1].entity_id in duplicate_ids

    def test_find_combined_duplicates(self, db, test_problems):
        """Комбинированный поиск"""
        detector = DuplicateDetector(similarity_threshold=0.5)
        problem = test_problems[0]

        duplicates = detector.find_combined_duplicates(db, problem, limit=10)

        # Вторая яма должна иметь высокий score (текст + локация)
        assert len(duplicates) > 0
        duplicate_ids = [p.entity_id for p, _ in duplicates]
        assert test_problems[1].entity_id in duplicate_ids

        # Проверяем что score выше для второй ямы чем для мусора
        scores = {p.entity_id: score for p, score in duplicates}
        if test_problems[2].entity_id in scores:
            assert scores[test_problems[1].entity_id] > scores[test_problems[2].entity_id]


class TestGetSimilarProblems:
    """Тесты API получения похожих проблем"""

    def test_get_similar_text_method(self, client, db, test_problems):
        """Получить похожие проблемы (текстовый метод)"""
        problem_id = test_problems[0].entity_id

        response = client.get(
            f"/api/v1/ai/similar-problems/{problem_id}?method=text&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] > 0

        # Проверяем структуру результата
        if data["items"]:
            item = data["items"][0]
            assert "problem" in item
            assert "similarity_score" in item
            assert 0 <= item["similarity_score"] <= 1

    def test_get_similar_location_method(self, client, db, test_problems):
        """Получить похожие проблемы (геолокация)"""
        problem_id = test_problems[0].entity_id

        response = client.get(
            f"/api/v1/ai/similar-problems/{problem_id}?method=location&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_similar_combined_method(self, client, db, test_problems):
        """Получить похожие проблемы (комбинированный)"""
        problem_id = test_problems[0].entity_id

        response = client.get(
            f"/api/v1/ai/similar-problems/{problem_id}?method=combined&limit=5"
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) <= 5

    def test_get_similar_invalid_method(self, client, test_problems):
        """Неверный метод"""
        problem_id = test_problems[0].entity_id

        response = client.get(
            f"/api/v1/ai/similar-problems/{problem_id}?method=invalid"
        )

        assert response.status_code == 400

    def test_get_similar_nonexistent_problem(self, client):
        """Похожие для несуществующей проблемы"""
        response = client.get("/api/v1/ai/similar-problems/99999")

        assert response.status_code == 404


class TestFindDuplicatesBeforeCreate:
    """Тесты поиска дубликатов перед созданием"""

    def test_find_duplicates_with_text_only(self, client, db, test_problems, auth_headers):
        """Поиск дубликатов только по тексту"""
        response = client.post(
            "/api/v1/ai/find-duplicates",
            json={
                "title": "Большая яма на дороге",
                "description": "На улице Ленина большая яма, нужен ремонт",
                "city": "Bishkek",
                "problem_type": "infrastructure",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Проверяем что API работает корректно
        assert isinstance(data["items"], list)

    def test_find_duplicates_with_location(self, client, db, test_problems, auth_headers):
        """Поиск дубликатов с геолокацией"""
        response = client.post(
            "/api/v1/ai/find-duplicates",
            json={
                "title": "Новая яма",
                "description": "Яма на дороге",
                "city": "Bishkek",
                "latitude": 42.8746,
                "longitude": 74.5698,
                "problem_type": "infrastructure",
                "tags": ["яма", "дорога"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_find_duplicates_no_matches(self, client, db, test_problems, auth_headers):
        """Поиск дубликатов без совпадений"""
        response = client.post(
            "/api/v1/ai/find-duplicates",
            json={
                "title": "Совершенно уникальная проблема xyz123",
                "description": "Абсолютно новая проблема которой нет",
                "city": "Bishkek",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Может быть 0 или очень низкий score
        assert "items" in data

    def test_find_duplicates_without_auth(self, client):
        """Поиск без авторизации"""
        response = client.post(
            "/api/v1/ai/find-duplicates",
            json={
                "title": "Test",
                "description": "Test",
                "city": "Bishkek",
            },
        )

        assert response.status_code == 401


class TestDuplicatesStats:
    """Тесты статистики дубликатов"""

    def test_get_duplicates_stats(self, client, db, test_problems):
        """Получить статистику дубликатов"""
        response = client.get(
            "/api/v1/ai/duplicates-stats?city=Bishkek&threshold=0.5"
        )

        assert response.status_code == 200
        data = response.json()
        assert "city" in data
        assert "total_problems" in data
        assert "potential_duplicates" in data
        assert "duplicate_groups" in data
        assert data["city"] == "Bishkek"
        assert data["total_problems"] > 0

    def test_get_duplicates_stats_empty_city(self, client, db):
        """Статистика для города без проблем"""
        response = client.get(
            "/api/v1/ai/duplicates-stats?city=EmptyCity&threshold=0.8"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_problems"] == 0
        assert data["potential_duplicates"] == 0

    def test_get_duplicates_stats_high_threshold(self, client, db, test_problems):
        """Статистика с высоким порогом"""
        response = client.get(
            "/api/v1/ai/duplicates-stats?city=Bishkek&threshold=0.95"
        )

        assert response.status_code == 200
        data = response.json()
        # С высоким порогом должно быть меньше дубликатов
        assert "duplicate_groups" in data
