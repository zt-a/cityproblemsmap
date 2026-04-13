# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import os
import redis

# Устанавливаем переменную окружения для отключения rate limiting
os.environ['TESTING'] = 'true'

# Мокируем limiter.limit ДО импорта приложения
def mock_limit_decorator(*args, **kwargs):
    """Декоратор-заглушка для rate limiting в тестах"""
    def decorator(func):
        return func
    return decorator

# Патчим limiter.limit перед импортом main
with patch('app.middleware.rate_limit.limiter.limit', side_effect=mock_limit_decorator):
    from app.main import app
    from app.database import Base, get_db
    from app.config import settings

# Переинициализируем redis_client с правильным URL для тестов
import app.services.redis_client as redis_module
redis_client = redis.from_url(settings.redis_url, decode_responses=True)
redis_module.redis_client = redis_client

# ── Тестовая БД ───────────────────────────────────────────
# Отдельная база чтобы тесты не трогали реальные данные
# TEST_DATABASE_URL = settings.DATABASE_URL.replace(
#     "/city_problems",
#     "/city_problems_test",
# )
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


def override_get_db():
    """
    Подменяет реальную БД тестовой.
    FastAPI вызывает эту функцию вместо get_db()
    для всех запросов в тестах.
    """
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подменяем dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE SEQUENCE IF NOT EXISTS entity_id_seq START 1;"))
        conn.commit()

    Base.metadata.create_all(bind=test_engine)

    # Seed достижений — нужны для test_get_achievements_list
    from app.models.gamification import Achievement
    db = TestSessionLocal()
    try:
        if db.query(Achievement).count() == 0:
            achievements = [
                Achievement(code="first_problem", name="Первая проблема", description="Создайте первую проблему", criteria={"problems_created": 1}, points=10, rarity="common"),
                Achievement(code="10_problems", name="10 проблем", description="Создайте 10 проблем", criteria={"problems_created": 10}, points=50, rarity="uncommon"),
                Achievement(code="active_citizen", name="Активный гражданин", description="Проголосуйте 100 раз", criteria={"votes_cast": 100}, points=100, rarity="rare"),
            ]
            for a in achievements:
                db.add(a)
            db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """
    Очищает все таблицы между тестами.
    autouse=True — применяется к каждому тесту автоматически.
    Порядок важен — сначала дочерние таблицы потом родительские.
    """
    yield
    db = TestSessionLocal()
    try:
        # Отключаем проверку внешних ключей для быстрой очистки
        db.execute(text("SET session_replication_role = 'replica';"))

        # Новые таблицы (геймификация, социальные, уведомления)
        tables_to_truncate = [
            "notifications", "user_notification_settings", "activities",
            "user_achievements", "user_levels", "user_challenges",
            "challenges", "follows", "user_profiles", # "achievements" убрали
            "reputation_logs", "votes", "comments", "problem_media",
            "reports", "subscriptions",  # Добавлены новые таблицы
            "simulation_events", "problems", "zones", "users"
        ]

        for table in tables_to_truncate:
            try:
                db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
            except Exception:
                # Таблица может не существовать
                pass

        # Включаем обратно проверку внешних ключей
        db.execute(text("SET session_replication_role = 'origin';"))

        # Сбросить sequence чтобы entity_id начинался с 1 в каждом тесте
        db.execute(text("ALTER SEQUENCE entity_id_seq RESTART WITH 1;"))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def db():
    """Сессия БД для прямого доступа в тестах."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """HTTP клиент для тестов — не нужен реальный сервер."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_redis_before_test():
    """Очищаем все ключи в Redis перед каждым тестом."""
    redis_client.flushall()

@pytest.fixture(scope="session", autouse=True)
def disable_rate_limiting_globally():
    """Полностью отключаем rate limiting для всех тестов"""
    from app.main import app
    from slowapi.errors import RateLimitExceeded

    # Удаляем обработчик rate limit ошибок
    if RateLimitExceeded in app.exception_handlers:
        del app.exception_handlers[RateLimitExceeded]

    # Удаляем limiter из state
    if hasattr(app.state, 'limiter'):
        delattr(app.state, 'limiter')

    yield

@pytest.fixture
def registered_user(client):
    """
    Готовый зарегистрированный пользователь с корректным email.
    """
    user_data = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123",
        "country": None,
        "city": "Bishkek",
        "district": None,
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    resp_json = response.json()
    # Убедимся, что email есть в user для тестов
    resp_json["user"]["email"] = user_data["email"]
    return resp_json


@pytest.fixture
def auth_headers(registered_user):
    """
    Заголовки с токеном для авторизованных запросов.
    Использование: client.get("/...", headers=auth_headers)
    """
    token = registered_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def registered_admin(client):
    """Зарегистрированный пользователь с ролью admin."""
    # Сначала создаём обычного юзера
    response = client.post("/api/v1/auth/register", json={
        "username": "adminuser",
        "email":    "admin@test.com",
        "password": "password123",
        "city":     "Bishkek",
    })
    assert response.status_code == 201
    data = response.json()

    # ВАЖНО: Используем отдельное подключение вне транзакции теста
    from sqlalchemy import create_engine
    from app.config import settings

    # Создаем новый engine для прямого доступа к БД
    direct_engine = create_engine(settings.TEST_DATABASE_URL)
    with direct_engine.connect() as conn:
        # Выполняем UPDATE вне транзакции теста
        conn.execute(
            text("UPDATE users SET role = :role WHERE entity_id = :entity_id AND is_current = true"),
            {"role": "admin", "entity_id": data["user"]["entity_id"]}
        )
        conn.commit()
    direct_engine.dispose()

    return data


@pytest.fixture
def admin_headers(registered_admin):
    """Заголовки с токеном админа."""
    token = registered_admin["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_celery_tasks():
    """
    Подменяем Celery .delay() на синхронный вызов.
    Так scores реально пересчитываются в тестах
    без подключения к Redis.
    """
    from app.services.scoring import recalculate_scores
    from app.services.zones import recalculate_zone_stats
    from app.database import SessionLocal

    def sync_recalculate_scores(problem_entity_id, changed_by_id):
        db = SessionLocal()
        try:
            recalculate_scores(
                db                = db,
                problem_entity_id = problem_entity_id,
                changed_by_id     = changed_by_id,
            )
        finally:
            db.close()

    def sync_update_zone_stats(zone_entity_id, changed_by_id):
        db = SessionLocal()
        try:
            recalculate_zone_stats(
                db             = db,
                zone_entity_id = zone_entity_id,
                changed_by_id  = changed_by_id,
            )
        finally:
            db.close()

    with patch(
        "app.workers.tasks_scoring.recalculate_problem_scores.delay",
        side_effect=sync_recalculate_scores,
    ), patch(
        "app.workers.tasks_zones.update_zone_stats.delay",
        side_effect=sync_update_zone_stats,
    ):
        yield