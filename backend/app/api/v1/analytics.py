# app/api/v1/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import (
    CityOverview, PeriodStats,
    HeatmapPoint, ZoneIndexes,
    ResponseTimeStats, CityDigitalTwin,
)
from app.services.analytics import (
    get_city_overview, get_period_trend,
    get_heatmap, get_zone_indexes,
    get_response_time_stats, get_city_digital_twin,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/cities/{city}/overview", response_model=CityOverview)
def city_overview(city: str, db: Session = Depends(get_db)):
    """
    Главная сводка по городу.
    Статусы, типы проблем, solve rate, активная зона.
    """
    return get_city_overview(db, city)


@router.get("/cities/{city}/trend", response_model=list[PeriodStats])
def city_trend(
    city: str,
    days: int     = Query(30, ge=7, le=365, description="Период в днях"),
    db:   Session = Depends(get_db),
):
    """
    Динамика активности за период.
    Новые проблемы, решённые, голоса, комментарии по дням.
    Используется для графиков на дашборде.
    """
    return get_period_trend(db, city, days)


@router.get("/cities/{city}/heatmap", response_model=list[HeatmapPoint])
def city_heatmap(city: str, db: Session = Depends(get_db)):
    """
    Данные тепловой карты — все активные проблемы с координатами и весом.
    Передаётся напрямую в Leaflet heatmap layer или MapboxGL.
    """
    return get_heatmap(db, city)


@router.get("/cities/{city}/zones", response_model=list[ZoneIndexes])
def city_zone_indexes(city: str, db: Session = Depends(get_db)):
    """
    Индексы всех зон города — pollution, traffic, risk.
    Используется для окрашивания районов на карте Digital Twin.
    Отсортированы по risk_score — самые опасные первыми.
    """
    return get_zone_indexes(db, city)


@router.get("/cities/{city}/response-time", response_model=ResponseTimeStats)
def city_response_time(city: str, db: Session = Depends(get_db)):
    """
    Статистика времени реакции властей/волонтёров.
    Среднее, минимальное, максимальное время решения проблем.
    Показывает насколько эффективно работают службы города.
    """
    return get_response_time_stats(db, city)


@router.get("/cities/{city}/digital-twin", response_model=CityDigitalTwin)
def city_digital_twin(city: str, db: Session = Depends(get_db)):
    """
    Полный Digital Twin срез города — все данные одним запросом.
    Используется для главного дашборда симуляций.

    Включает:
    - Сводку по городу
    - Индексы всех зон
    - Тепловую карту
    - Время реакции властей
    - Тренд за 30 дней
    """
    return get_city_digital_twin(db, city)