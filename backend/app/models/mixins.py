# app/models/mixins.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, DateTime, String, text
from sqlalchemy.orm import Session


def utc_now():
    """Возвращает timezone-aware datetime для SQLAlchemy default"""
    return datetime.now(timezone.utc)


class VersionMixin:
    """
    Подмешивается во все версионируемые модели.

    Правило: только INSERT. Никакого UPDATE кроме
    пометки is_current=False на старой версии.
    """

    id            = Column(Integer, primary_key=True, index=True)
    entity_id     = Column(Integer, nullable=False, index=True)
    version       = Column(Integer, nullable=False, default=1)
    is_current    = Column(Boolean, nullable=False, default=True, index=True)
    created_at    = Column(DateTime, default=utc_now, nullable=False)
    superseded_at = Column(DateTime, nullable=True)
    change_reason = Column(String(300), nullable=True)
    changed_by_id = Column(Integer, nullable=True)  # entity_id юзера

    @classmethod
    def next_entity_id(cls, db: Session) -> int:
        """Берёт следующий глобальный entity_id из sequence."""
        result = db.execute(text("SELECT nextval('entity_id_seq')"))
        return result.scalar()