# app/schemas/ai.py
from pydantic import BaseModel, Field
from typing import List
from app.schemas.problem import ProblemPublic


class DuplicateResult(BaseModel):
    problem: ProblemPublic
    similarity_score: float = Field(..., description="Оценка сходства от 0 до 1")


class DuplicatesList(BaseModel):
    items: List[DuplicateResult]
    total: int


class FindDuplicatesRequest(BaseModel):
    title: str
    description: str
    city: str
    latitude: float | None = None
    longitude: float | None = None
    problem_type: str | None = None
    tags: List[str] | None = None
