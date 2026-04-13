# app/schemas/analytics_extended.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ZoneComparison(BaseModel):
    """Сравнение двух или более зон"""
    zone_id: int
    zone_name: str
    total_problems: int
    open_problems: int
    solved_problems: int
    solve_rate: float
    avg_priority: float
    avg_response_days: float
    pollution_index: float
    traffic_index: float
    risk_score: float


class TopZone(BaseModel):
    """Топ проблемных зон"""
    zone_entity_id: int
    zone_name: str
    zone_type: str
    open_problems: int
    risk_score: float
    avg_priority: float
    rank: int


class UserLeaderboard(BaseModel):
    """Рейтинг активных пользователей"""
    user_entity_id: int
    username: str
    problems_created: int
    problems_solved: int  # Для волонтёров
    comments_count: int
    votes_count: int
    reputation: float
    rank: int


class OfficialEfficiency(BaseModel):
    """Эффективность официальных лиц"""
    user_entity_id: int
    username: str
    assigned_problems: int
    solved_problems: int
    avg_response_days: float
    solve_rate: float
    rank: int


class ProblemTrend(BaseModel):
    """Тренд по типу проблемы"""
    problem_type: str
    date: str
    count: int
    avg_priority: float


class ExportFormat(BaseModel):
    """Формат экспорта данных"""
    format: str  # csv, excel, pdf
    data_type: str  # problems, zones, users, analytics
    filters: Optional[dict] = None


class AnalyticsPrediction(BaseModel):
    """Прогноз проблемных зон (ML)"""
    zone_entity_id: int
    zone_name: str
    current_risk_score: float
    predicted_risk_score: float
    prediction_confidence: float
    factors: list[str]  # Факторы, влияющие на прогноз


class TimeSeriesData(BaseModel):
    """Временные ряды для графиков"""
    date: str
    value: float
    label: str


class ZoneHeatmapData(BaseModel):
    """Данные для тепловой карты зон"""
    zone_entity_id: int
    zone_name: str
    center_lat: float
    center_lon: float
    intensity: float  # 0-1
    problem_count: int
    color: str  # hex color based on intensity
