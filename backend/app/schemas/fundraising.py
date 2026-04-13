# app/schemas/fundraising.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FundraisingCreate(BaseModel):
    goal_amount: float = Field(..., gt=0, description="Целевая сумма")
    currency: str = Field(default="KGS", description="Валюта")
    deadline: Optional[datetime] = Field(None, description="Дедлайн сбора")
    description: Optional[str] = Field(None, description="Описание сбора")


class FundraisingPublic(BaseModel):
    entity_id: int
    version: int
    is_current: bool
    created_at: datetime
    problem_entity_id: int
    goal_amount: float
    current_amount: float
    currency: str
    deadline: Optional[datetime]
    status: str
    description: Optional[str]
    progress_percent: float = 0.0

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.goal_amount > 0:
            self.progress_percent = round((self.current_amount / self.goal_amount) * 100, 2)


class DonationCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма пожертвования")
    currency: str = Field(default="KGS", description="Валюта")
    is_anonymous: bool = Field(default=False, description="Анонимное пожертвование")
    message: Optional[str] = Field(None, max_length=500, description="Сообщение")


class DonationPublic(BaseModel):
    entity_id: int
    version: int
    created_at: datetime
    fundraising_entity_id: int
    donor_entity_id: Optional[int]
    amount: float
    currency: str
    is_anonymous: bool
    message: Optional[str]

    class Config:
        from_attributes = True


class DonationsList(BaseModel):
    items: list[DonationPublic]
    total: int
    total_amount: float


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма расхода")
    currency: str = Field(default="KGS", description="Валюта")
    description: str = Field(..., description="Описание расхода")
    receipt_url: Optional[str] = Field(None, description="Ссылка на чек")


class ExpensePublic(BaseModel):
    entity_id: int
    version: int
    created_at: datetime
    fundraising_entity_id: int
    amount: float
    currency: str
    description: str
    receipt_url: Optional[str]
    approved_by_entity_id: Optional[int]

    class Config:
        from_attributes = True


class ExpensesList(BaseModel):
    items: list[ExpensePublic]
    total: int
    total_spent: float
