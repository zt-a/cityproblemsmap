# app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# Движок подключения к PostgreSQL
engine = create_engine(
    settings.db_url,
    # Количество постоянных соединений в пуле
    pool_size=20,
    # Дополнительные соединения сверх pool_size если все заняты
    max_overflow=40,
    
    pool_timeout=30,

    pool_recycle=3600,
    # Проверять соединение перед использованием (на случай если БД перезапустилась)
    pool_pre_ping=True,
)

# Фабрика сессий — каждый запрос получает свою сессию
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # транзакции подтверждаем вручную через db.commit()
    autoflush=False,    # не отправлять SQL до явного flush/commit
)


# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency для FastAPI.
    Открывает сессию на время запроса, закрывает после — даже если была ошибка.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Вызывается при старте приложения.
    Создаёт расширение PostGIS и sequence для entity_id.
    """
    with engine.connect() as conn:
        # PostGIS — геопространственные типы (POINT, POLYGON и т.д.)
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

        # Глобальный счётчик entity_id для всех таблиц
        # Так entity_id уникален across users, problems, zones и т.д.
        conn.execute(text("CREATE SEQUENCE IF NOT EXISTS entity_id_seq START 1;"))

        conn.commit()