# tests/test_reports.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.models.comment import Comment
from app.models.report import Report
from app.services.auth import create_access_token, hash_password


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """Создать обычного пользователя"""
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
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def moderator_user(db: Session):
    """Создать модератора"""
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
def test_comment(db: Session, test_problem, test_user):
    """Создать тестовый комментарий"""
    entity_id = Comment.next_entity_id(db)
    comment = Comment(
        entity_id=entity_id,
        version=1,
        is_current=True,
        problem_entity_id=test_problem.entity_id,
        author_entity_id=test_user.entity_id,
        content="Test comment",
        comment_type="user",
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


class TestCreateReport:
    """Тесты создания жалоб"""

    def test_create_report_on_problem_success(self, client, db, test_problem, auth_headers):
        """Успешная жалоба на проблему"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "problem",
                "target_entity_id": test_problem.entity_id,
                "reason": "spam",
                "description": "This is spam content",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "problem"
        assert data["target_entity_id"] == test_problem.entity_id
        assert data["reason"] == "spam"
        assert data["status"] == "pending"

    def test_create_report_on_comment_success(self, client, db, test_comment, auth_headers):
        """Успешная жалоба на комментарий"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "comment",
                "target_entity_id": test_comment.entity_id,
                "reason": "offensive",
                "description": "Offensive language",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "comment"
        assert data["reason"] == "offensive"

    def test_create_report_on_user_success(self, client, db, moderator_user, auth_headers):
        """Успешная жалоба на пользователя"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "user",
                "target_entity_id": moderator_user.entity_id,
                "reason": "inappropriate",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "user"

    def test_create_report_on_self(self, client, test_user, auth_headers):
        """Нельзя пожаловаться на самого себя"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "user",
                "target_entity_id": test_user.entity_id,
                "reason": "spam",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "самого себя" in response.json()["detail"]

    def test_create_duplicate_report(self, client, db, test_problem, test_user, auth_headers):
        """Нельзя создать дубликат жалобы"""
        # Создаем первую жалобу
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        # Пытаемся создать вторую
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "problem",
                "target_entity_id": test_problem.entity_id,
                "reason": "spam",
            },
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert "уже пожаловались" in response.json()["detail"]

    def test_create_report_nonexistent_target(self, client, auth_headers):
        """Жалоба на несуществующую цель"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "problem",
                "target_entity_id": 99999,
                "reason": "spam",
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_create_report_without_auth(self, client, test_problem):
        """Жалоба без авторизации"""
        response = client.post(
            "/api/v1/reports/",
            json={
                "target_type": "problem",
                "target_entity_id": test_problem.entity_id,
                "reason": "spam",
            },
        )

        assert response.status_code == 401


class TestGetMyReports:
    """Тесты получения своих жалоб"""

    def test_get_my_reports(self, client, db, test_problem, test_user, auth_headers):
        """Получить свои жалобы"""
        # Создаем жалобу
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        response = client.get("/api/v1/reports/my", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["entity_id"] == entity_id

    def test_get_my_reports_filtered(self, client, db, test_problem, test_user, auth_headers):
        """Получить свои жалобы с фильтром"""
        # Создаем жалобы с разными статусами
        for status in ["pending", "resolved"]:
            entity_id = Report.next_entity_id(db)
            report = Report(
                entity_id=entity_id,
                version=1,
                is_current=True,
                reporter_entity_id=test_user.entity_id,
                target_type="problem",
                target_entity_id=test_problem.entity_id,
                reason="spam",
                status=status,
            )
            db.add(report)
        db.commit()

        response = client.get(
            "/api/v1/reports/my?status_filter=pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "pending"


class TestModerationQueue:
    """Тесты очереди модерации"""

    def test_get_moderation_queue(self, client, db, test_problem, test_user, moderator_headers):
        """Получить очередь модерации"""
        # Создаем жалобы
        for i in range(3):
            entity_id = Report.next_entity_id(db)
            report = Report(
                entity_id=entity_id,
                version=1,
                is_current=True,
                reporter_entity_id=test_user.entity_id,
                target_type="problem",
                target_entity_id=test_problem.entity_id,
                reason="spam",
                status="pending",
            )
            db.add(report)
        db.commit()

        response = client.get(
            "/api/v1/reports/moderation/queue",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_get_moderation_queue_unauthorized(self, client, auth_headers):
        """Обычный пользователь не может получить очередь"""
        response = client.get(
            "/api/v1/reports/moderation/queue",
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_get_moderation_queue_filtered(self, client, db, test_problem, test_user, moderator_headers):
        """Очередь с фильтром по типу"""
        # Создаем жалобы разных типов
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        response = client.get(
            "/api/v1/reports/moderation/queue?target_type=problem",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert all(item["target_type"] == "problem" for item in data["items"])


class TestResolveReport:
    """Тесты разрешения жалоб"""

    def test_resolve_report_success(self, client, db, test_problem, test_user, moderator_user, moderator_headers):
        """Успешное разрешение жалобы"""
        # Создаем жалобу
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        response = client.patch(
            f"/api/v1/reports/moderation/{entity_id}/resolve",
            json={
                "status": "resolved",
                "resolution_note": "Confirmed spam, removed",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolved_by_entity_id"] == moderator_user.entity_id
        assert data["resolution_note"] == "Confirmed spam, removed"
        assert data["version"] == 2

    def test_reject_report_success(self, client, db, test_problem, test_user, moderator_headers):
        """Успешное отклонение жалобы"""
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        response = client.patch(
            f"/api/v1/reports/moderation/{entity_id}/resolve",
            json={
                "status": "rejected",
                "resolution_note": "Not spam",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    def test_resolve_already_resolved(self, client, db, test_problem, test_user, moderator_headers):
        """Нельзя разрешить уже обработанную жалобу"""
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="resolved",
        )
        db.add(report)
        db.commit()

        response = client.patch(
            f"/api/v1/reports/moderation/{entity_id}/resolve",
            json={"status": "resolved"},
            headers=moderator_headers,
        )

        assert response.status_code == 400
        assert "уже обработана" in response.json()["detail"]

    def test_resolve_unauthorized(self, client, db, test_problem, test_user, auth_headers):
        """Обычный пользователь не может разрешать жалобы"""
        entity_id = Report.next_entity_id(db)
        report = Report(
            entity_id=entity_id,
            version=1,
            is_current=True,
            reporter_entity_id=test_user.entity_id,
            target_type="problem",
            target_entity_id=test_problem.entity_id,
            reason="spam",
            status="pending",
        )
        db.add(report)
        db.commit()

        response = client.patch(
            f"/api/v1/reports/moderation/{entity_id}/resolve",
            json={"status": "resolved"},
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestModerationStats:
    """Тесты статистики модерации"""

    def test_get_moderation_stats(self, client, db, test_problem, test_user, moderator_headers):
        """Получить статистику жалоб"""
        # Создаем жалобы с разными статусами
        statuses = ["pending", "pending", "reviewed", "resolved", "rejected"]
        for status in statuses:
            entity_id = Report.next_entity_id(db)
            report = Report(
                entity_id=entity_id,
                version=1,
                is_current=True,
                reporter_entity_id=test_user.entity_id,
                target_type="problem",
                target_entity_id=test_problem.entity_id,
                reason="spam",
                status=status,
            )
            db.add(report)
        db.commit()

        response = client.get(
            "/api/v1/reports/moderation/stats",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pending"] == 2
        assert data["reviewed"] == 1
        assert data["resolved"] == 1
        assert data["rejected"] == 1
        assert "by_target_type" in data

    def test_get_stats_unauthorized(self, client, auth_headers):
        """Обычный пользователь не может получить статистику"""
        response = client.get(
            "/api/v1/reports/moderation/stats",
            headers=auth_headers,
        )

        assert response.status_code == 403
