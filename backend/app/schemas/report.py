# app/schemas/report.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ReportCreate(BaseModel):
    target_type: str = Field(..., description="Тип цели: problem/comment/user")
    target_entity_id: int = Field(..., description="ID цели")
    reason: str = Field(..., description="Причина: spam/offensive/inappropriate/other")
    description: Optional[str] = Field(None, description="Дополнительное описание")


class ReportResolve(BaseModel):
    status: str = Field(..., description="Статус: resolved/rejected")
    resolution_note: Optional[str] = Field(None, description="Примечание модератора")


class ReportPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: int
    version: int
    is_current: bool
    created_at: datetime
    reporter_entity_id: int
    target_type: str
    target_entity_id: int
    reason: str
    description: Optional[str]
    status: str
    resolved_by_entity_id: Optional[int]
    resolution_note: Optional[str]
    problem_entity_id: Optional[int] = Field(None, description="ID проблемы (для comment reports)")



class ReportList(BaseModel):
    items: list[ReportPublic]
    total: int
    offset: int
    limit: int
