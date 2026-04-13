# tests/test_duplicates.py
import pytest

DUPLICATES_URL = "/api/v1/duplicates"

VALID_PROBLEM = {
    "title": "Яма на дороге",
    "description": "Большая яма на пересечении улиц",
    "country": "Kyrgyzstan",
    "city": "Bishkek",
    "district": "Первомайский",
    "address": "ул. Манаса 50",
    "latitude": 42.8746,
    "longitude": 74.5698,
    "problem_type": "pothole",
    "nature": "permanent",
    "tags": ["asphalt", "road"],
}


@pytest.fixture
def created_problem(client, auth_headers):
    """Создаёт проблему в БД для тестов дубликатов."""
    response = client.post(
        "/api/v1/problems/",
        json=VALID_PROBLEM,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestCheckDuplicates:

    def test_check_no_duplicates(self, client):
        """Проверка когда дубликатов нет."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8746,
                "lon": 74.5698,
                "problem_type": "pothole",
                "title": "Яма на дороге",
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["has_duplicates"] is False
        assert data["duplicates"] == []
        assert "не найдено" in data["message"].lower()

    def test_check_with_duplicate_nearby(self, client, auth_headers, created_problem):
        """Проверка находит дубликат рядом (в радиусе 200м)."""
        # Создаём похожую проблему очень близко (разница ~10м)
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8747,  # Очень близко к 42.8746
                "lon": 74.5699,  # Очень близко к 74.5698
                "problem_type": "pothole",
                "title": "Большая яма на дороге",
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["has_duplicates"] is True
        assert len(data["duplicates"]) >= 1

        duplicate = data["duplicates"][0]
        assert duplicate["entity_id"] == created_problem["entity_id"]
        assert duplicate["similarity"] >= 0.7
        assert duplicate["distance_m"] < 200
        assert "похожих проблем" in data["message"].lower()

    def test_check_different_type_no_duplicate(self, client, auth_headers, created_problem):
        """Разный тип проблемы - не дубликат."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8746,
                "lon": 74.5698,
                "problem_type": "garbage",  # Другой тип
                "title": "Яма на дороге",
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Не должно найти дубликат т.к. тип другой
        assert data["has_duplicates"] is False

    def test_check_far_away_no_duplicate(self, client, auth_headers, created_problem):
        """Далеко (>200м) - не дубликат."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8800,  # ~600м от оригинала
                "lon": 74.5800,
                "problem_type": "pothole",
                "title": "Яма на дороге",
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["has_duplicates"] is False

    def test_check_custom_threshold(self, client, auth_headers, created_problem):
        """Проверка с кастомным порогом похожести."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8747,
                "lon": 74.5699,
                "problem_type": "pothole",
                "title": "Совсем другое название",
                "threshold": 0.3,  # Низкий порог
            }
        )
        assert response.status_code == 200
        data = response.json()

        # С низким порогом может найти
        assert "duplicates" in data

    def test_check_missing_params(self, client):
        """Проверка без обязательных параметров - 422."""
        response = client.get(f"{DUPLICATES_URL}/check")
        assert response.status_code == 422

    def test_check_invalid_coordinates(self, client):
        """Проверка с невалидными координатами."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 200,  # Невалидная широта
                "lon": 74.5698,
                "problem_type": "pothole",
                "title": "Яма",
            }
        )
        # Должно вернуть ошибку валидации или пустой результат
        assert response.status_code in [200, 422]

    def test_check_short_title(self, client):
        """Проверка с коротким заголовком - 422."""
        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8746,
                "lon": 74.5698,
                "problem_type": "pothole",
                "title": "Я",  # Меньше 3 символов
            }
        )
        assert response.status_code == 422

    def test_check_multiple_duplicates(self, client, auth_headers):
        """Проверка находит несколько дубликатов."""
        # Создаём 3 похожие проблемы рядом
        for i in range(3):
            client.post(
                "/api/v1/problems/",
                json={
                    **VALID_PROBLEM,
                    "latitude": 42.8746 + i * 0.0001,
                    "longitude": 74.5698 + i * 0.0001,
                    "title": f"Яма на дороге {i}",
                },
                headers=auth_headers,
            )

        response = client.get(
            f"{DUPLICATES_URL}/check",
            params={
                "lat": 42.8746,
                "lon": 74.5698,
                "problem_type": "pothole",
                "title": "Яма на дороге",
                "threshold": 0.5,
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert data["has_duplicates"] is True
        assert len(data["duplicates"]) >= 2

        # Проверяем что дубликаты отсортированы по similarity
        similarities = [d["similarity"] for d in data["duplicates"]]
        assert similarities == sorted(similarities, reverse=True)
