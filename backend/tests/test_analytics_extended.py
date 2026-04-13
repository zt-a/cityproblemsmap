# tests/test_analytics_extended.py
import pytest
from fastapi.testclient import TestClient


def test_compare_zones(client: TestClient, auth_headers):
    """Тест сравнения зон"""
    from app.database import SessionLocal
    from app.models.zone import Zone

    # Создаем несколько зон
    db = SessionLocal()
    try:
        zone1 = Zone(
            entity_id=1,
            version=1,
            is_current=True,
            name="Zone 1",
            zone_type="district",
            city="Bishkek",
            country="Kyrgyzstan",
            total_problems=10,
            open_problems=5,
            solved_problems=5,
            risk_score=0.5,
            changed_by_id=1,
        )
        zone2 = Zone(
            entity_id=2,
            version=1,
            is_current=True,
            name="Zone 2",
            zone_type="district",
            city="Bishkek",
            country="Kyrgyzstan",
            total_problems=20,
            open_problems=15,
            solved_problems=5,
            risk_score=0.75,
            changed_by_id=1,
        )
        db.add(zone1)
        db.add(zone2)
        db.commit()
    finally:
        db.close()

    # Сравниваем зоны
    response = client.get("/api/v1/analytics/zones/comparison?zone_ids=1,2", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["zone_id"] == 1
    assert data[1]["zone_id"] == 2


def test_compare_zones_invalid_format(client: TestClient, auth_headers):
    """Тест сравнения зон с неверным форматом"""
    response = client.get("/api/v1/analytics/zones/comparison?zone_ids=abc,def", headers=auth_headers)
    assert response.status_code == 400
    assert "Invalid zone IDs format" in response.json()["detail"]


def test_compare_zones_too_few(client: TestClient, auth_headers):
    """Тест сравнения с недостаточным количеством зон"""
    response = client.get("/api/v1/analytics/zones/comparison?zone_ids=1", headers=auth_headers)
    assert response.status_code == 400
    assert "At least 2 zones required" in response.json()["detail"]


def test_compare_zones_too_many(client: TestClient, auth_headers):
    """Тест сравнения со слишком большим количеством зон"""
    zone_ids = ",".join(str(i) for i in range(1, 12))
    response = client.get(f"/api/v1/analytics/zones/comparison?zone_ids={zone_ids}", headers=auth_headers)
    assert response.status_code == 400
    assert "Maximum 10 zones" in response.json()["detail"]


def test_top_problematic_zones(client: TestClient, auth_headers):
    """Тест получения топ проблемных зон"""
    from app.database import SessionLocal
    from app.models.zone import Zone

    # Создаем зоны с разными уровнями проблем
    db = SessionLocal()
    try:
        for i in range(5):
            zone = Zone(
                entity_id=i + 1,
                version=1,
                is_current=True,
                name=f"Zone {i + 1}",
                zone_type="district",
                city="Bishkek",
                country="Kyrgyzstan",
                total_problems=10 * (i + 1),
                open_problems=5 * (i + 1),
                solved_problems=5 * (i + 1),
                risk_score=0.1 * (i + 1),
                changed_by_id=1,
            )
            db.add(zone)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/analytics/zones/top?city=Bishkek&limit=3", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) <= 3


def test_user_leaderboard(client: TestClient, auth_headers):
    """Тест рейтинга пользователей"""
    response = client.get("/api/v1/analytics/leaderboard/users?city=Bishkek&limit=10", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_user_leaderboard_with_period(client: TestClient, auth_headers):
    """Тест рейтинга пользователей за период"""
    response = client.get(
        "/api/v1/analytics/leaderboard/users?city=Bishkek&limit=10&period_days=7",
        headers=auth_headers
    )
    assert response.status_code == 200


def test_officials_efficiency(client: TestClient, auth_headers):
    """Тест эффективности официальных лиц"""
    response = client.get("/api/v1/analytics/leaderboard/officials?city=Bishkek&limit=10", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_problem_trends_by_type(client: TestClient, auth_headers):
    """Тест трендов по типам проблем"""
    response = client.get("/api/v1/analytics/trends/by-type?city=Bishkek&days=30", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


def test_export_problems_csv(client: TestClient, auth_headers):
    """Тест экспорта проблем в CSV"""
    from app.database import SessionLocal
    from app.models.problem import Problem, ProblemStatus, ProblemType, ProblemNature
    from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

    # Создаем проблему
    db = SessionLocal()
    try:
        location = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)
        problem = Problem(
            entity_id=1,
            version=1,
            is_current=True,
            title="Test Problem",
            description="Test Description",
            status=ProblemStatus.open,
            problem_type=ProblemType.infrastructure,
            nature=ProblemNature.permanent,
            city="Bishkek",
            country="Kyrgyzstan",
            location=location,
            author_entity_id=1,
            changed_by_id=1,
        )
        db.add(problem)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/analytics/export/problems?city=Bishkek&format=csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]

    # Проверяем содержимое CSV
    content = response.text
    assert "ID" in content
    assert "Title" in content
    assert "Test Problem" in content


def test_export_problems_json(client: TestClient, auth_headers):
    """Тест экспорта проблем в JSON"""
    from app.database import SessionLocal
    from app.models.problem import Problem, ProblemStatus, ProblemType, ProblemNature
    from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

    # Создаем проблему
    db = SessionLocal()
    try:
        location = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)
        problem = Problem(
            entity_id=1,
            version=1,
            is_current=True,
            title="Test Problem",
            description="Test Description",
            status=ProblemStatus.open,
            problem_type=ProblemType.infrastructure,
            nature=ProblemNature.permanent,
            city="Bishkek",
            country="Kyrgyzstan",
            location=location,
            author_entity_id=1,
            changed_by_id=1,
        )
        db.add(problem)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/analytics/export/problems?city=Bishkek&format=json", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test Problem"


def test_export_problems_with_status_filter(client: TestClient, auth_headers):
    """Тест экспорта проблем с фильтром по статусу"""
    from app.database import SessionLocal
    from app.models.problem import Problem, ProblemStatus, ProblemType, ProblemNature
    from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

    # Создаем проблемы с разными статусами
    db = SessionLocal()
    try:
        location1 = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)
        problem1 = Problem(
            entity_id=1,
            version=1,
            is_current=True,
            title="Open Problem",
            description="Test",
            status=ProblemStatus.open,
            problem_type=ProblemType.infrastructure,
            nature=ProblemNature.permanent,
            city="Bishkek",
            country="Kyrgyzstan",
            location=location1,
            author_entity_id=1,
            changed_by_id=1,
        )
        location2 = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)
        problem2 = Problem(
            entity_id=2,
            version=1,
            is_current=True,
            title="Solved Problem",
            description="Test",
            status=ProblemStatus.solved,
            problem_type=ProblemType.infrastructure,
            nature=ProblemNature.permanent,
            city="Bishkek",
            country="Kyrgyzstan",
            location=location2,
            author_entity_id=1,
            changed_by_id=1,
        )
        db.add(problem1)
        db.add(problem2)
        db.commit()
    finally:
        db.close()

    response = client.get(
        "/api/v1/analytics/export/problems?city=Bishkek&format=json&status=open",
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "open"


def test_export_zones_csv(client: TestClient, auth_headers):
    """Тест экспорта зон в CSV"""
    from app.database import SessionLocal
    from app.models.zone import Zone

    # Создаем зону
    db = SessionLocal()
    try:
        zone = Zone(
            entity_id=1,
            version=1,
            is_current=True,
            name="Test Zone",
            zone_type="district",
            city="Bishkek",
            country="Kyrgyzstan",
            total_problems=10,
            open_problems=5,
            solved_problems=5,
            risk_score=0.5,
            changed_by_id=1,
        )
        db.add(zone)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/analytics/export/zones?city=Bishkek&format=csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    content = response.text
    assert "Test Zone" in content


def test_export_zones_json(client: TestClient, auth_headers):
    """Тест экспорта зон в JSON"""
    from app.database import SessionLocal
    from app.models.zone import Zone

    # Создаем зону
    db = SessionLocal()
    try:
        zone = Zone(
            entity_id=1,
            version=1,
            is_current=True,
            name="Test Zone",
            zone_type="district",
            city="Bishkek",
            country="Kyrgyzstan",
            total_problems=10,
            open_problems=5,
            solved_problems=5,
            risk_score=0.5,
            changed_by_id=1,
        )
        db.add(zone)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/analytics/export/zones?city=Bishkek&format=json", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Zone"


def test_export_users_csv(client: TestClient, auth_headers):
    """Тест экспорта пользователей в CSV"""
    response = client.get("/api/v1/analytics/export/users?city=Bishkek&format=csv", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

    content = response.text
    assert "Username" in content


def test_export_users_json(client: TestClient, auth_headers):
    """Тест экспорта пользователей в JSON"""
    response = client.get("/api/v1/analytics/export/users?city=Bishkek&format=json", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_analytics_unauthorized(client: TestClient):
    """Тест доступа к аналитике без авторизации"""
    response = client.get("/api/v1/analytics/zones/comparison?zone_ids=1,2")
    assert response.status_code == 401

    response = client.get("/api/v1/analytics/zones/top?city=Bishkek")
    assert response.status_code == 401

    response = client.get("/api/v1/analytics/leaderboard/users?city=Bishkek")
    assert response.status_code == 401
