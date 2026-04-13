# tests/test_versioning.py
import pytest
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from app.models.problem import Problem, ProblemStatus, ProblemType
from app.services.versioning import (
    read_geospatial,
    read_with_custom_filters,
    count_with_custom_filters,
)


@pytest.fixture
def problems_in_db(client, auth_headers):
    """Создаёт несколько проблем для тестов."""
    problems = []
    locations = [
        (42.8746, 74.5698),
        (42.8750, 74.5700),
        (42.8800, 74.5800),
    ]

    for i, (lat, lon) in enumerate(locations):
        response = client.post(
            "/api/v1/problems/",
            json={
                "title": f"Проблема {i}",
                "description": "Описание",
                "country": "Kyrgyzstan",
                "city": "Bishkek",
                "district": "Первомайский",
                "address": f"ул. Манаса {i}",
                "latitude": lat,
                "longitude": lon,
                "problem_type": "pothole" if i < 2 else "garbage",
                "nature": "permanent",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        problems.append(response.json())

    return problems


class TestReadGeospatial:

    def test_read_geospatial_basic(self, db, problems_in_db):
        """Базовый тест read_geospatial."""
        point = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)

        results = read_geospatial(
            db=db,
            model_class=Problem,
            filters={"problem_type": ProblemType.pothole},
            geospatial_filters=[
                ST_DWithin(Problem.location, point, 0.001)  # ~111 метров в градусах
            ],
            limit=10
        )

        assert isinstance(results, list)
        # Должна найти хотя бы одну проблему
        assert len(results) >= 1

        # Все результаты должны быть pothole
        for problem in results:
            assert problem.problem_type == ProblemType.pothole

    def test_read_geospatial_with_distance_sort(self, db, problems_in_db):
        """Сортировка по расстоянию."""
        point = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)

        results = read_geospatial(
            db=db,
            model_class=Problem,
            filters={},
            geospatial_filters=[
                ST_DWithin(Problem.location, point, 0.1)  # ~11 км в градусах
            ],
            order_by=func.ST_Distance(Problem.location, point),
            limit=10
        )

        assert len(results) >= 2
        # Первая проблема должна быть ближе всех
        assert results[0].title == "Проблема 0"

    def test_read_geospatial_no_results(self, db, problems_in_db):
        """Нет результатов в радиусе."""
        # Точка далеко от всех проблем
        point = ST_SetSRID(ST_MakePoint(80.0, 50.0), 4326)

        results = read_geospatial(
            db=db,
            model_class=Problem,
            filters={},
            geospatial_filters=[
                ST_DWithin(Problem.location, point, 0.001)  # ~111 метров в градусах
            ],
            limit=10
        )

        assert results == []

    def test_read_geospatial_pagination(self, db, problems_in_db):
        """Пагинация работает."""
        point = ST_SetSRID(ST_MakePoint(74.5698, 42.8746), 4326)

        # Первая страница
        page1 = read_geospatial(
            db=db,
            model_class=Problem,
            filters={},
            geospatial_filters=[
                ST_DWithin(Problem.location, point, 0.1)  # ~11 км в градусах
            ],
            limit=1,
            offset=0
        )

        # Вторая страница
        page2 = read_geospatial(
            db=db,
            model_class=Problem,
            filters={},
            geospatial_filters=[
                ST_DWithin(Problem.location, point, 0.1)  # ~11 км в градусах
            ],
            limit=1,
            offset=1
        )

        assert len(page1) == 1
        assert len(page2) == 1
        assert page1[0].entity_id != page2[0].entity_id


class TestReadWithCustomFilters:

    def test_read_with_custom_filters_basic(self, db, problems_in_db):
        """Базовый тест read_with_custom_filters."""
        results = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.problem_type == ProblemType.pothole
            ],
            limit=10
        )

        assert isinstance(results, list)
        assert len(results) >= 1

        # Все результаты должны быть pothole
        for problem in results:
            assert problem.problem_type == ProblemType.pothole

    def test_read_with_custom_filters_multiple(self, db, problems_in_db):
        """Несколько фильтров."""
        results = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.problem_type == ProblemType.pothole,
                Problem.status == ProblemStatus.open,
            ],
            limit=10
        )

        assert isinstance(results, list)
        for problem in results:
            assert problem.problem_type == ProblemType.pothole
            assert problem.status == ProblemStatus.open

    def test_read_with_custom_filters_in_operator(self, db, problems_in_db):
        """Фильтр с IN оператором."""
        results = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.problem_type.in_([ProblemType.pothole, ProblemType.garbage])
            ],
            limit=10
        )

        assert len(results) >= 2

    def test_read_with_custom_filters_order_by(self, db, problems_in_db):
        """Сортировка работает."""
        results = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[],
            order_by=Problem.created_at.desc(),
            limit=10
        )

        assert len(results) >= 2
        # Последняя созданная должна быть первой
        assert results[0].title == "Проблема 2"

    def test_read_with_custom_filters_pagination(self, db, problems_in_db):
        """Пагинация работает."""
        page1 = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[],
            limit=1,
            offset=0
        )

        page2 = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[],
            limit=1,
            offset=1
        )

        assert len(page1) == 1
        assert len(page2) == 1
        assert page1[0].entity_id != page2[0].entity_id

    def test_read_with_custom_filters_empty(self, db, problems_in_db):
        """Пустые фильтры возвращают все записи."""
        results = read_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[],
            limit=10
        )

        assert len(results) == 3


class TestCountWithCustomFilters:

    def test_count_with_custom_filters_basic(self, db, problems_in_db):
        """Базовый тест count_with_custom_filters."""
        count = count_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.problem_type == ProblemType.pothole
            ]
        )

        assert isinstance(count, int)
        assert count == 2  # Две проблемы с типом pothole

    def test_count_with_custom_filters_multiple(self, db, problems_in_db):
        """Несколько фильтров."""
        count = count_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.problem_type == ProblemType.pothole,
                Problem.status == ProblemStatus.open,
            ]
        )

        assert count == 2

    def test_count_with_custom_filters_no_results(self, db, problems_in_db):
        """Нет результатов."""
        count = count_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[
                Problem.status == ProblemStatus.solved
            ]
        )

        assert count == 0

    def test_count_with_custom_filters_empty(self, db, problems_in_db):
        """Пустые фильтры считают все записи."""
        count = count_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=[]
        )

        assert count == 3

    def test_count_with_custom_filters_none(self, db, problems_in_db):
        """None фильтры считают все записи."""
        count = count_with_custom_filters(
            db=db,
            model_class=Problem,
            custom_filters=None
        )

        assert count == 3
