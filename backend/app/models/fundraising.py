# app/models/fundraising.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.models.mixins import VersionMixin
from app.database import Base


class Fundraising(VersionMixin, Base):
    __tablename__ = "fundraisings"

    problem_entity_id = Column(Integer, nullable=False, index=True)
    goal_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="KGS")
    deadline = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active/completed/cancelled
    description = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<Fundraising(entity_id={self.entity_id}, "
            f"problem={self.problem_entity_id}, "
            f"goal={self.goal_amount}, "
            f"current={self.current_amount})>"
        )


class Donation(VersionMixin, Base):
    __tablename__ = "donations"

    fundraising_entity_id = Column(Integer, nullable=False, index=True)
    donor_entity_id = Column(Integer, nullable=True)  # None для анонимных
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="KGS")
    is_anonymous = Column(Integer, nullable=False, default=False)
    message = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<Donation(entity_id={self.entity_id}, "
            f"fundraising={self.fundraising_entity_id}, "
            f"amount={self.amount})>"
        )


class FundraisingExpense(VersionMixin, Base):
    __tablename__ = "fundraising_expenses"

    fundraising_entity_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="KGS")
    description = Column(Text, nullable=False)
    receipt_url = Column(String(500), nullable=True)
    approved_by_entity_id = Column(Integer, nullable=True)

    def __repr__(self):
        return (
            f"<FundraisingExpense(entity_id={self.entity_id}, "
            f"fundraising={self.fundraising_entity_id}, "
            f"amount={self.amount})>"
        )
