# tests/test_analytics.py
import pytest

ANALYTICS_URL = "/api/v1/analytics"
PROBLEMS_URL  = "/api/v1/problems"
ZONES_URL     = "/api/v1/zones"
REGISTER_URL  = "/api/v1/auth/register"

VALID_PROBLEM = {
    "title":        "Яма на дороге",
    "country":      "Kyrgyzstan",
    "city":         "Bishkek",
    "latitude":     42.8746,
    "longitude":    74.5698,
    "problem_type": "pothole",
    "nature":       "permanent",
}

VALID_ZONE = {
    "name":       "Первомайский район",
    "zone_type":  "district",
    "country":    "Kyrgyzstan",
    "city":       "Bishkek",
    "center_lat": 42.8746,
    "center_lon": 74.5698,
}


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def city():
    return "Bishkek"


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
def created_zone(client, admin_headers):
    response = client.post(
        ZONES_URL + "/",
        json=VALID_ZONE,
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_user(client):
    response = client.post(REGISTER_URL, json={
        "username": "analyst",
        "email":    "analyst@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_headers(second_user):
    return {"Authorization": f"Bearer {second_user['access_token']}"}


class TestCityOverview:

    def test_overview_empty_city(self, client, city):
        """Сводка по городу без проблем — всё нули."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/overview")

        assert response.status_code == 200
        data = response.json()

        assert data["city"]           == city
        assert data["total_problems"] == 0
        assert data["solve_rate"]     == 0.0
        assert data["by_type"]        == []

        dist = data["status_distribution"]
        assert dist["total"]       == 0
        assert dist["open"]        == 0
        assert dist["solved"]      == 0

    def test_overview_with_problems(self, client, city, created_problem):
        """Сводка с одной проблемой."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/overview")

        assert response.status_code == 200
        data = response.json()

        assert data["total_problems"] == 1
        assert data["status_distribution"]["open"] == 1

        # Тип проблемы есть в by_type
        types = [t["problem_type"] for t in data["by_type"]]
        assert "pothole" in types

    def test_overview_solve_rate(self, client, city, created_problem, auth_headers):
        """
        solve_rate = solved / total.
        Создаём проблему и решаем её — solve_rate = 1.0.
        """
        pid = created_problem["entity_id"]
        client.patch(
            f"{PROBLEMS_URL}/{pid}/status",
            json={"status": "solved"},
            headers=auth_headers,
        )

        response = client.get(f"{ANALYTICS_URL}/cities/{city}/overview")
        data     = response.json()

        assert data["solve_rate"]                       == 1.0
        assert data["status_distribution"]["solved"]    == 1
        assert data["status_distribution"]["open"]      == 0

    def test_overview_multiple_problem_types(
        self, client, city, auth_headers
    ):
        """Несколько типов проблем в by_type."""
        # Создаём разные типы проблем
        for problem_type in ["pothole", "garbage", "flooding"]:
            client.post(
                PROBLEMS_URL + "/",
                json={**VALID_PROBLEM, "problem_type": problem_type},
                headers=auth_headers,
            )

        response = client.get(f"{ANALYTICS_URL}/cities/{city}/overview")
        data     = response.json()

        assert data["total_problems"] == 3
        assert len(data["by_type"])   == 3

        # by_type отсортирован по количеству — у каждого по 1
        types = {t["problem_type"] for t in data["by_type"]}
        assert "pothole"  in types
        assert "garbage"  in types
        assert "flooding" in types


class TestCityTrend:

    def test_trend_returns_30_days(self, client, city):
        """Тренд за 30 дней — ровно 30 записей."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/trend",
            params={"days": 30},
        )
        assert response.status_code == 200
        assert len(response.json()) == 30

    def test_trend_returns_7_days(self, client, city):
        """Тренд за 7 дней — ровно 7 записей."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/trend",
            params={"days": 7},
        )
        assert response.status_code == 200
        assert len(response.json()) == 7

    def test_trend_structure(self, client, city):
        """Каждая запись тренда имеет нужные поля."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/trend")
        data     = response.json()

        # Проверяем структуру первого элемента
        first = data[0]
        assert "date"           in first
        assert "new_problems"   in first
        assert "solved"         in first
        assert "total_votes"    in first
        assert "total_comments" in first

    def test_trend_today_has_problem(self, client, city, created_problem):
        """
        После создания проблемы — в сегодняшней записи тренда
        new_problems > 0.
        """
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/trend",
            params={"days": 7},
        )
        data = response.json()

        # Последний день = сегодня
        today = data[-1]
        assert today["new_problems"] == 1

    def test_trend_invalid_days(self, client, city):
        """days меньше 7 — 422."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/trend",
            params={"days": 3},
        )
        assert response.status_code == 422


class TestCityHeatmap:

    def test_heatmap_empty(self, client, city):
        """Тепловая карта без проблем — пустой список."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/heatmap")

        assert response.status_code == 200
        assert response.json()      == []

    def test_heatmap_with_problem(self, client, city, created_problem):
        """После создания проблемы — одна точка на карте."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/heatmap")

        assert response.status_code == 200
        points = response.json()
        assert len(points) == 1

        point = points[0]
        assert "latitude"      in point
        assert "longitude"     in point
        assert "weight"        in point
        assert "problem_count" in point

        # Координаты совпадают с проблемой
        assert abs(point["latitude"]  - VALID_PROBLEM["latitude"])  < 0.001
        assert abs(point["longitude"] - VALID_PROBLEM["longitude"]) < 0.001

    def test_heatmap_solved_problem_excluded(
        self, client, city, created_problem, auth_headers
    ):
        """
        Решённые проблемы не попадают в тепловую карту.
        Heatmap показывает только open и in_progress.
        """
        pid = created_problem["entity_id"]
        client.patch(
            f"{PROBLEMS_URL}/{pid}/status",
            json={"status": "solved"},
            headers=auth_headers,
        )

        response = client.get(f"{ANALYTICS_URL}/cities/{city}/heatmap")
        assert response.json() == []


class TestCityZoneIndexes:

    def test_zone_indexes_empty(self, client, city):
        """Нет зон — пустой список."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/zones")

        assert response.status_code == 200
        assert response.json()      == []

    def test_zone_indexes_with_zone(self, client, city, created_zone):
        """После создания зоны — один элемент."""
        response = client.get(f"{ANALYTICS_URL}/cities/{city}/zones")

        assert response.status_code == 200
        zones = response.json()
        assert len(zones) == 1

        zone = zones[0]
        assert "zone_entity_id"  in zone
        assert "zone_name"       in zone
        assert "pollution_index" in zone
        assert "traffic_index"   in zone
        assert "risk_score"      in zone
        assert "solve_rate"      in zone

    def test_zone_indexes_sorted_by_risk(self, client, city, admin_headers):
        """Зоны отсортированы по risk_score — самые опасные первыми."""
        # Создаём две зоны
        client.post(ZONES_URL + "/", json={
            **VALID_ZONE, "name": "Зона A"
        }, headers=admin_headers)
        client.post(ZONES_URL + "/", json={
            **VALID_ZONE, "name": "Зона B"
        }, headers=admin_headers)

        response = client.get(f"{ANALYTICS_URL}/cities/{city}/zones")
        zones    = response.json()

        # Проверяем что отсортировано по убыванию risk_score
        scores = [z["risk_score"] for z in zones]
        assert scores == sorted(scores, reverse=True)


class TestResponseTime:

    def test_response_time_no_solved(self, client, city):
        """Нет решённых проблем — все нули."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/response-time"
        )
        assert response.status_code == 200
        data = response.json()

        assert data["total_solved"]       == 0
        assert data["avg_days_to_solve"]  == 0.0
        assert data["fastest_solve_days"] == 0.0
        assert data["slowest_solve_days"] == 0.0

    def test_response_time_with_solved(
        self, client, city, created_problem, auth_headers
    ):
        """После решения проблемы — total_solved = 1."""
        pid = created_problem["entity_id"]
        client.patch(
            f"{PROBLEMS_URL}/{pid}/status",
            json={"status": "solved"},
            headers=auth_headers,
        )

        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/response-time"
        )
        data = response.json()

        assert data["total_solved"]      == 1
        assert data["avg_days_to_solve"] >= 0.0


class TestDigitalTwin:

    def test_digital_twin_structure(self, client, city):
        """Digital Twin возвращает все необходимые поля."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/digital-twin"
        )
        assert response.status_code == 200
        data = response.json()

        assert "city"          in data
        assert "snapshot_at"   in data
        assert "overview"      in data
        assert "zone_indexes"  in data
        assert "heatmap"       in data
        assert "response_time" in data
        assert "period_trend"  in data

        assert data["city"]              == city
        assert len(data["period_trend"]) == 30

    def test_digital_twin_empty_city(self, client, city):
        """Digital Twin пустого города — корректные нули."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/digital-twin"
        )
        data = response.json()

        assert data["overview"]["total_problems"] == 0
        assert data["heatmap"]                    == []
        assert data["zone_indexes"]               == []

    def test_digital_twin_with_data(
        self, client, city, created_problem, created_zone
    ):
        """Digital Twin с данными — heatmap не пустой."""
        response = client.get(
            f"{ANALYTICS_URL}/cities/{city}/digital-twin"
        )
        data = response.json()

        assert data["overview"]["total_problems"] == 1
        assert len(data["heatmap"])               == 1
        assert len(data["zone_indexes"])          == 1