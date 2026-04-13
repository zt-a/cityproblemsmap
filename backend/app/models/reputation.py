# app/models/reputation.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from app.database import Base


def utc_now():
    """Возвращает timezone-aware datetime для SQLAlchemy default"""
    return datetime.now(timezone.utc)


# Единственная модель БЕЗ VersionMixin —
# она сама по себе immutable журнал событий.
# Каждая строка = неизменный факт.
class ReputationLog(Base):
    __tablename__ = "reputation_logs"

    id                        = Column(Integer, primary_key=True, index=True)
    user_entity_id            = Column(Integer, nullable=False, index=True)

    delta                     = Column(Float,       nullable=False)
    reason                    = Column(String(100), nullable=False)
    note                      = Column(Text,        nullable=True)

    related_problem_entity_id = Column(Integer, nullable=True)
    related_vote_entity_id    = Column(Integer, nullable=True)

    # Репутация ПОСЛЕ delta — история без JOIN-ов
    snapshot_reputation       = Column(Float,    nullable=False)
    created_at                = Column(DateTime, default=utc_now, nullable=False)