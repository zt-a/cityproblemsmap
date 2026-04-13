# app/schemas/analytics.py
from pydantic import BaseModel
from datetime import datetime


# ── Базовая аналитика ─────────────────────────────────────

class ProblemTypeStats(BaseModel):
    """Статистика по типу проблемы."""
    problem_type: str
    total:        int
    open:         int
    solved:       int
    rejected:     int
    avg_priority: float


class StatusDistribution(BaseModel):
    """Распределение проблем по статусам."""
    open:        int
    in_progress: int
    solved:      int
    rejected:    int
    archived:    int
    total:       int


class CityOverview(BaseModel):
    """
    Общая сводка по городу.
    Главный экран дашборда.
    """
    city:                str
    total_problems:      int
    status_distribution: StatusDistribution
    by_type:             list[ProblemTypeStats]
    avg_priority_score:  float
    avg_truth_score:     float
    most_active_zone:    str | None   # название зоны с макс. проблемами
    solve_rate:          float        # solved / total


class PeriodStats(BaseModel):
    """Динамика за период — для графиков."""
    date:           str    # "2024-01-15"
    new_problems:   int
    solved:         int
    total_votes:    int
    total_comments: int


# ── Digital Twin аналитика ────────────────────────────────

class HeatmapPoint(BaseModel):
    """
    Одна точка тепловой карты.
    Фронт рисует heatmap из этих точек.
    """
    latitude:       float
    longitude:      float
    weight:         float   # интенсивность точки 0.0–1.0
    problem_count:  int
    avg_priority:   float


class ZoneIndexes(BaseModel):
    """Индексы зоны для Digital Twin."""
    zone_entity_id:  int
    zone_name:       str
    zone_type:       str
    center_lat:      float | None
    center_lon:      float | None
    pollution_index: float
    traffic_index:   float
    risk_score:      float
    open_problems:   int
    solve_rate:      float


class ResponseTimeStats(BaseModel):
    """
    Время реакции властей/волонтёров.
    open → in_progress → solved
    """
    avg_days_to_start:  float   # open → in_progress
    avg_days_to_solve:  float   # open → solved
    fastest_solve_days: float
    slowest_solve_days: float
    total_solved:       int


class CityDigitalTwin(BaseModel):
    """
    Полный Digital Twin срез города.
    Всё что нужно для симуляций и AI.
    """
    city:              str
    snapshot_at:       datetime
    overview:          CityOverview
    zone_indexes:      list[ZoneIndexes]
    heatmap:           list[HeatmapPoint]
    response_time:     ResponseTimeStats
    period_trend:      list[PeriodStats]   # последние 30 дней