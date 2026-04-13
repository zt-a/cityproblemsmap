# tests/test_fundraising.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.main import app
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.models.fundraising import Fundraising, Donation, FundraisingExpense
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
def test_problem(db: Session, test_user):
    entity_id = Problem.next_entity_id(db)
    problem = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        changed_by_entity_id=test_user.entity_id,
        title="Тестовая проблема",
        description="Описание проблемы",
        category="infrastructure",
        status="open",
        location="POINT(74.5698 42.8746)",
        country="Kyrgyzstan",
        city="Bishkek",
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(test_user.entity_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def moderator_headers(moderator_user):
    token = create_access_token(moderator_user.entity_id)
    return {"Authorization": f"Bearer {token}"}



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestCreateFundraising:
    """Тесты создания сбора средств"""

    def test_create_fundraising_success(self, client, db, test_problem, moderator_headers):
        """Успешное создание сбора средств"""
        response = client.post(
            f"/api/v1/fundraising/problems/{test_problem.entity_id}/fundraising",
            json={
                "goal_amount": 100000.0,
                "currency": "KGS",
                "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "description": "Сбор на ремонт дороги",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["problem_entity_id"] == test_problem.entity_id
        assert data["goal_amount"] == 100000.0
        assert data["current_amount"] == 0.0
        assert data["status"] == "active"
        assert data["currency"] == "KGS"

    def test_create_fundraising_unauthorized(self, client, test_problem, auth_headers):
        """Обычный пользователь не может создать сбор"""
        response = client.post(
            f"/api/v1/fundraising/problems/{test_problem.entity_id}/fundraising",
            json={
                "goal_amount": 100000.0,
                "currency": "KGS",
            },
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_create_fundraising_problem_not_found(self, client, moderator_headers):
        """Создание сбора для несуществующей проблемы"""
        response = client.post(
            "/api/v1/fundraising/problems/99999/fundraising",
            json={
                "goal_amount": 100000.0,
                "currency": "KGS",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 404

    def test_create_fundraising_duplicate(self, client, db, test_problem, moderator_user, moderator_headers):
        """Нельзя создать второй активный сбор для проблемы"""
        # Создаем первый сбор
        entity_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=entity_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=50000.0,
            current_amount=0.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        # Пытаемся создать второй
        response = client.post(
            f"/api/v1/fundraising/problems/{test_problem.entity_id}/fundraising",
            json={
                "goal_amount": 100000.0,
                "currency": "KGS",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 409



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestGetFundraising:
    """Тесты получения информации о сборе"""

    def test_get_fundraising_success(self, client, db, test_problem, moderator_user):
        """Успешное получение информации о сборе"""
        # Создаем сбор
        entity_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=entity_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=25000.0,
            currency="KGS",
            status="active",
            description="Тестовый сбор",
        )
        db.add(fundraising)
        db.commit()

        response = client.get(
            f"/api/v1/fundraising/problems/{test_problem.entity_id}/fundraising"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["entity_id"] == entity_id
        assert data["goal_amount"] == 100000.0
        assert data["current_amount"] == 25000.0
        assert data["progress_percent"] == 25.0

    def test_get_fundraising_not_found(self, client, test_problem):
        """Сбор не найден"""
        response = client.get(
            f"/api/v1/fundraising/problems/{test_problem.entity_id}/fundraising"
        )

        assert response.status_code == 404



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestMakeDonation:
    """Тесты создания пожертвований"""

    def test_make_donation_success(self, client, db, test_problem, moderator_user, test_user, auth_headers):
        """Успешное пожертвование"""
        # Создаем сбор
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=0.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/donate",
            json={
                "amount": 5000.0,
                "currency": "KGS",
                "is_anonymous": False,
                "message": "Спасибо за работу!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 5000.0
        assert data["fundraising_entity_id"] == fundraising_id
        assert data["donor_entity_id"] == test_user.entity_id
        assert data["is_anonymous"] is False

        # Проверяем, что сумма обновилась
        db.refresh(fundraising)
        updated = db.query(Fundraising).filter(
            Fundraising.entity_id == fundraising_id,
            Fundraising.is_current == True
        ).first()
        assert updated.current_amount == 5000.0

    def test_make_donation_anonymous(self, client, db, test_problem, moderator_user, auth_headers):
        """Анонимное пожертвование"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=0.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/donate",
            json={
                "amount": 1000.0,
                "currency": "KGS",
                "is_anonymous": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["donor_entity_id"] is None
        assert data["is_anonymous"] is True

    def test_make_donation_completes_fundraising(self, client, db, test_problem, moderator_user, auth_headers):
        """Пожертвование завершает сбор при достижении цели"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=10000.0,
            current_amount=9000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/donate",
            json={
                "amount": 1500.0,
                "currency": "KGS",
                "is_anonymous": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Проверяем статус
        updated = db.query(Fundraising).filter(
            Fundraising.entity_id == fundraising_id,
            Fundraising.is_current == True
        ).first()
        assert updated.status == "completed"
        assert updated.current_amount == 10500.0

    def test_make_donation_inactive_fundraising(self, client, db, test_problem, moderator_user, auth_headers):
        """Нельзя пожертвовать в неактивный сбор"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=0.0,
            currency="KGS",
            status="cancelled",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/donate",
            json={
                "amount": 1000.0,
                "currency": "KGS",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_make_donation_not_found(self, client, auth_headers):
        """Пожертвование в несуществующий сбор"""
        response = client.post(
            "/api/v1/fundraising/99999/donate",
            json={
                "amount": 1000.0,
                "currency": "KGS",
            },
            headers=auth_headers,
        )

        assert response.status_code == 404



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestGetDonations:
    """Тесты получения списка пожертвований"""

    def test_get_donations_list(self, client, db, test_problem, moderator_user, test_user):
        """Получить список пожертвований"""
        # Создаем сбор
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=0.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        # Создаем пожертвования
        for i in range(3):
            donation_id = Donation.next_entity_id(db)
            donation = Donation(
                entity_id=donation_id,
                version=1,
                is_current=True,
                changed_by_entity_id=test_user.entity_id,
                fundraising_entity_id=fundraising_id,
                donor_entity_id=test_user.entity_id,
                amount=1000.0 * (i + 1),
                currency="KGS",
                is_anonymous=False,
            )
            db.add(donation)
        db.commit()

        response = client.get(f"/api/v1/fundraising/{fundraising_id}/donations")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["total_amount"] == 6000.0
        assert len(data["items"]) == 3

    def test_get_donations_pagination(self, client, db, test_problem, moderator_user, test_user):
        """Пагинация списка пожертвований"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=0.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        # Создаем 5 пожертвований
        for i in range(5):
            donation_id = Donation.next_entity_id(db)
            donation = Donation(
                entity_id=donation_id,
                version=1,
                is_current=True,
                changed_by_entity_id=test_user.entity_id,
                fundraising_entity_id=fundraising_id,
                donor_entity_id=test_user.entity_id,
                amount=1000.0,
                currency="KGS",
                is_anonymous=False,
            )
            db.add(donation)
        db.commit()

        response = client.get(
            f"/api/v1/fundraising/{fundraising_id}/donations?skip=2&limit=2"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestAddExpense:
    """Тесты добавления расходов"""

    def test_add_expense_success(self, client, db, test_problem, moderator_user, moderator_headers):
        """Успешное добавление расхода"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/expenses",
            json={
                "amount": 15000.0,
                "currency": "KGS",
                "description": "Покупка материалов",
                "receipt_url": "https://example.com/receipt.pdf",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 15000.0
        assert data["description"] == "Покупка материалов"
        assert data["receipt_url"] == "https://example.com/receipt.pdf"
        assert data["approved_by_entity_id"] == moderator_user.entity_id

    def test_add_expense_unauthorized(self, client, db, test_problem, moderator_user, auth_headers):
        """Обычный пользователь не может добавить расход"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.post(
            f"/api/v1/fundraising/{fundraising_id}/expenses",
            json={
                "amount": 15000.0,
                "currency": "KGS",
                "description": "Покупка материалов",
            },
            headers=auth_headers,
        )

        assert response.status_code == 403

    def test_add_expense_not_found(self, client, moderator_headers):
        """Добавление расхода к несуществующему сбору"""
        response = client.post(
            "/api/v1/fundraising/99999/expenses",
            json={
                "amount": 15000.0,
                "currency": "KGS",
                "description": "Покупка материалов",
            },
            headers=moderator_headers,
        )

        assert response.status_code == 404



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestGetExpenses:
    """Тесты получения списка расходов"""

    def test_get_expenses_list(self, client, db, test_problem, moderator_user):
        """Получить список расходов"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        # Создаем расходы
        for i in range(3):
            expense_id = FundraisingExpense.next_entity_id(db)
            expense = FundraisingExpense(
                entity_id=expense_id,
                version=1,
                is_current=True,
                changed_by_entity_id=moderator_user.entity_id,
                fundraising_entity_id=fundraising_id,
                amount=5000.0 * (i + 1),
                currency="KGS",
                description=f"Расход {i + 1}",
                approved_by_entity_id=moderator_user.entity_id,
            )
            db.add(expense)
        db.commit()

        response = client.get(f"/api/v1/fundraising/{fundraising_id}/expenses")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["total_spent"] == 30000.0
        assert len(data["items"]) == 3



@pytest.mark.skip(reason="fundraising endpoints временно отключены")
class TestUpdateFundraisingStatus:
    """Тесты обновления статуса сбора"""

    def test_update_status_success(self, client, db, test_problem, moderator_user, moderator_headers):
        """Успешное обновление статуса"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.patch(
            f"/api/v1/fundraising/{fundraising_id}/status?status=cancelled",
            headers=moderator_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

        # Проверяем в БД
        updated = db.query(Fundraising).filter(
            Fundraising.entity_id == fundraising_id,
            Fundraising.is_current == True
        ).first()
        assert updated.status == "cancelled"

    def test_update_status_invalid(self, client, db, test_problem, moderator_user, moderator_headers):
        """Недопустимый статус"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.patch(
            f"/api/v1/fundraising/{fundraising_id}/status?status=invalid",
            headers=moderator_headers,
        )

        assert response.status_code == 400

    def test_update_status_unauthorized(self, client, db, test_problem, moderator_user, auth_headers):
        """Обычный пользователь не может обновить статус"""
        fundraising_id = Fundraising.next_entity_id(db)
        fundraising = Fundraising(
            entity_id=fundraising_id,
            version=1,
            is_current=True,
            changed_by_entity_id=moderator_user.entity_id,
            problem_entity_id=test_problem.entity_id,
            goal_amount=100000.0,
            current_amount=50000.0,
            currency="KGS",
            status="active",
        )
        db.add(fundraising)
        db.commit()

        response = client.patch(
            f"/api/v1/fundraising/{fundraising_id}/status?status=cancelled",
            headers=auth_headers,
        )

        assert response.status_code == 403
