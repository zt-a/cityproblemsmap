# app/models/vote.py
from sqlalchemy import Column, Integer, Float, Boolean, UniqueConstraint
from app.database import Base
from app.models.mixins import VersionMixin


class Vote(VersionMixin, Base):
    __tablename__ = "votes"

    problem_entity_id = Column(Integer, nullable=False, index=True)
    user_entity_id    = Column(Integer, nullable=False, index=True)

    is_true           = Column(Boolean, nullable=True)  # None = воздержался
    urgency           = Column(Integer, nullable=True)  # 1–5
    impact            = Column(Integer, nullable=True)  # 1–5
    inconvenience     = Column(Integer, nullable=True)  # 1–5

    # Снэпшот репутации на момент голосования — фиксируется навсегда
    weight            = Column(Float, default=1.0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "problem_entity_id", "user_entity_id", "is_current",
            name="uq_vote_current"
        ),
    )