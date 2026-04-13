# tests/test_ai.py
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def test_problem(client, auth_headers):
    """Создать тестовую проблему"""
    problem_data = {
        "title": "Разбитая дорога на улице Ленина",
        "description": "Большая яма на дороге, опасно для автомобилей",
        "city": "Bishkek",
        "problem_type": "roads",
        "latitude": 42.8746,
        "longitude": 74.5698,
        "tags": ["дорога", "яма"]
    }
    response = client.post("/api/v1/problems/", json=problem_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def similar_problem(client, auth_headers):
    """Создать похожую проблему"""
    problem_data = {
        "title": "Яма на дороге улица Ленина",
        "description": "Разбитое дорожное покрытие, нужен ремонт",
        "city": "Bishkek",
        "problem_type": "roads",
        "latitude": 42.8750,
        "longitude": 74.5700,
        "tags": ["дорога", "ремонт"]
    }
    response = client.post("/api/v1/problems/", json=problem_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def test_get_similar_problems_text_method(client, test_problem, similar_problem):
    """Поиск похожих проблем по тексту"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "text", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_get_similar_problems_location_method(client, test_problem, similar_problem):
    """Поиск похожих проблем по геолокации"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "location", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data


def test_get_similar_problems_combined_method(client, test_problem, similar_problem):
    """Поиск похожих проблем комбинированным методом"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "combined", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data

    # Проверяем структуру результата
    if data["items"]:
        item = data["items"][0]
        assert "problem" in item
        assert "similarity_score" in item
        assert 0 <= item["similarity_score"] <= 1


def test_get_similar_problems_invalid_method(client, test_problem):
    """Поиск с неверным методом"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "invalid"}
    )
    assert response.status_code == 400
    assert "Неверный метод" in response.json()["detail"]


def test_get_similar_problems_not_found(client):
    """Поиск похожих для несуществующей проблемы"""
    response = client.get("/api/v1/ai/similar-problems/99999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]


def test_get_similar_problems_limit(client, test_problem):
    """Проверка лимита результатов"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5


def test_find_duplicates_before_create(client, auth_headers, test_problem):
    """Поиск дубликатов перед созданием проблемы"""
    request_data = {
        "title": "Разбитая дорога на Ленина",
        "description": "Яма на дороге",
        "city": "Bishkek",
        "problem_type": "roads",
        "latitude": 42.8746,
        "longitude": 74.5698,
        "tags": ["дорога"]
    }

    response = client.post(
        "/api/v1/ai/find-duplicates",
        json=request_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_find_duplicates_without_location(client, auth_headers, test_problem):
    """Поиск дубликатов без геолокации"""
    request_data = {
        "title": "Разбитая дорога",
        "description": "Нужен ремонт",
        "city": "Bishkek",
        "problem_type": "roads",
        "tags": ["дорога"]
    }

    response = client.post(
        "/api/v1/ai/find-duplicates",
        json=request_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_find_duplicates_unauthorized(client):
    """Попытка поиска дубликатов без авторизации"""
    request_data = {
        "title": "Test",
        "description": "Test",
        "city": "Bishkek",
        "problem_type": "roads"
    }

    response = client.post("/api/v1/ai/find-duplicates", json=request_data)
    assert response.status_code == 401


def test_get_duplicates_stats(client, test_problem, similar_problem):
    """Получение статистики дубликатов"""
    response = client.get(
        "/api/v1/ai/duplicates-stats",
        params={"city": "Bishkek", "threshold": 0.7}
    )
    assert response.status_code == 200
    data = response.json()

    assert "city" in data
    assert "total_problems" in data
    assert "potential_duplicates" in data
    assert "duplicate_groups" in data
    assert data["city"] == "Bishkek"
    assert isinstance(data["duplicate_groups"], list)


def test_get_duplicates_stats_empty_city(client):
    """Статистика для города без проблем"""
    response = client.get(
        "/api/v1/ai/duplicates-stats",
        params={"city": "NonExistentCity"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_problems"] == 0
    assert data["potential_duplicates"] == 0
    assert data["duplicate_groups"] == []


def test_get_duplicates_stats_custom_threshold(client, test_problem):
    """Статистика с пользовательским порогом"""
    response = client.get(
        "/api/v1/ai/duplicates-stats",
        params={"city": "Bishkek", "threshold": 0.9}
    )
    assert response.status_code == 200
    data = response.json()
    assert "duplicate_groups" in data


def test_get_duplicates_stats_missing_city(client):
    """Статистика без указания города"""
    response = client.get("/api/v1/ai/duplicates-stats")
    assert response.status_code == 422  # Validation error


@patch("app.api.v1.ai.DuplicateDetector")
def test_similar_problems_with_mocked_detector(mock_detector_class, client, test_problem):
    """Тест с мокированным детектором дубликатов"""
    mock_detector = MagicMock()
    mock_detector.find_combined_duplicates.return_value = []
    mock_detector_class.return_value = mock_detector

    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "combined"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_find_duplicates_with_all_fields(client, auth_headers):
    """Поиск дубликатов со всеми полями"""
    request_data = {
        "title": "Полное описание проблемы",
        "description": "Детальное описание с множеством деталей",
        "city": "Bishkek",
        "problem_type": "infrastructure",
        "latitude": 42.8746,
        "longitude": 74.5698,
        "tags": ["инфраструктура", "ремонт", "срочно"]
    }

    response = client.post(
        "/api/v1/ai/find-duplicates",
        json=request_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_similar_problems_result_structure(client, test_problem, similar_problem):
    """Проверка структуры результата поиска похожих проблем"""
    response = client.get(
        f"/api/v1/ai/similar-problems/{test_problem['entity_id']}",
        params={"method": "combined", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()

    if data["items"]:
        item = data["items"][0]
        assert "problem" in item
        assert "similarity_score" in item

        problem = item["problem"]
        assert "entity_id" in problem
        assert "title" in problem
        assert "description" in problem
        assert "city" in problem
