# app/models/report.py
from sqlalchemy import Column, Integer, String, Boolean, Text
from app.models.mixins import VersionMixin
from app.database import Base


class Report(VersionMixin, Base):
    __tablename__ = "reports"

    reporter_entity_id = Column(Integer, nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # problem/comment/user
    target_entity_id = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)  # spam/offensive/inappropriate/other
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending/reviewed/resolved/rejected
    resolved_by_entity_id = Column(Integer, nullable=True)
    resolution_note = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<Report(entity_id={self.entity_id}, "
            f"target={self.target_type}:{self.target_entity_id}, "
            f"status={self.status})>"
        )
