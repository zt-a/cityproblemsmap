# app/services/analytics.py
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from geoalchemy2.functions import ST_X, ST_Y

from app.models.problem import Problem, ProblemStatus
from app.models.vote import Vote
from app.models.comment import Comment
from app.models.zone import Zone
from app.schemas.analytics import (
    ProblemTypeStats, StatusDistribution, CityOverview,
    PeriodStats, HeatmapPoint, ZoneIndexes,
    ResponseTimeStats, CityDigitalTwin,
)


# ── Базовая аналитика ─────────────────────────────────────

def get_status_distribution(
    db:   Session,
    city: str,
) -> StatusDistribution:
    """Распределение проблем по статусам в городе."""

    # Один запрос с GROUP BY вместо пяти отдельных COUNT
    rows = (
        db.query(Problem.status, func.count(Problem.id))
        .filter_by(city=city, is_current=True)
        .group_by(Problem.status)
        .all()
    )

    counts = {row[0].value: row[1] for row in rows}
    total  = sum(counts.values())

    return StatusDistribution(
        open        = counts.get("open",        0),
        in_progress = counts.get("in_progress", 0),
        solved      = counts.get("solved",      0),
        rejected    = counts.get("rejected",    0),
        archived    = counts.get("archived",    0),
        total       = total,
    )


def get_by_type_stats(
    db:   Session,
    city: str,
) -> list[ProblemTypeStats]:
    """Статистика по каждому типу проблемы."""

    # Агрегируем всё в одном запросе через CASE WHEN
    rows = (
        db.query(
            Problem.problem_type,
            func.count(Problem.id).label("total"),
            func.sum(
                case((Problem.status == ProblemStatus.open, 1), else_=0)
            ).label("open"),
            func.sum(
                case((Problem.status == ProblemStatus.solved, 1), else_=0)
            ).label("solved"),
            func.sum(
                case((Problem.status == ProblemStatus.rejected, 1), else_=0)
            ).label("rejected"),
            func.avg(Problem.priority_score).label("avg_priority"),
        )
        .filter_by(city=city, is_current=True)
        .group_by(Problem.problem_type)
        .order_by(func.count(Problem.id).desc())
        .all()
    )

    return [
        ProblemTypeStats(
            problem_type = row.problem_type.value,
            total        = row.total,
            open         = row.open or 0,
            solved       = row.solved or 0,
            rejected     = row.rejected or 0,
            avg_priority = round(float(row.avg_priority or 0), 4),
        )
        for row in rows
    ]


def get_city_overview(db: Session, city: str) -> CityOverview:
    """Главная сводка по городу."""

    status_dist = get_status_distribution(db, city)
    by_type     = get_by_type_stats(db, city)

    total = status_dist.total

    # Средние scores по городу
    scores = (
        db.query(
            func.avg(Problem.priority_score).label("avg_priority"),
            func.avg(Problem.truth_score).label("avg_truth"),
        )
        .filter_by(city=city, is_current=True)
        .first()
    )

    # Зона с максимальным количеством открытых проблем
    most_active = (
        db.query(Zone.name)
        .join(Problem, Zone.entity_id == Problem.zone_entity_id)
        .filter(
            Problem.city       == city,
            Problem.is_current,
            Problem.status     == ProblemStatus.open,
            Zone.is_current,
        )
        .group_by(Zone.name)
        .order_by(func.count(Problem.id).desc())
        .first()
    )

    solve_rate = (
        status_dist.solved / total if total > 0 else 0.0
    )

    return CityOverview(
        city                = city,
        total_problems      = total,
        status_distribution = status_dist,
        by_type             = by_type,
        avg_priority_score  = round(float(scores.avg_priority or 0), 4),
        avg_truth_score     = round(float(scores.avg_truth    or 0), 4),
        most_active_zone    = most_active[0] if most_active else None,
        solve_rate          = round(solve_rate, 4),
    )


def get_period_trend(
    db:   Session,
    city: str,
    days: int = 30,
) -> list[PeriodStats]:
    """
    Динамика по дням за последние N дней.
    Используется для графиков на дашборде.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Новые проблемы по дням — только version=1 (первое создание)
    new_by_day = (
        db.query(
            func.date(Problem.created_at).label("date"),
            func.count(Problem.id).label("count"),
        )
        .filter(
            Problem.city      == city,
            Problem.version   == 1,        # только первые версии = новые проблемы
            Problem.created_at >= since,
        )
        .group_by(func.date(Problem.created_at))
        .all()
    )

    # Решённые по дням — версии где статус стал solved
    solved_by_day = (
        db.query(
            func.date(Problem.created_at).label("date"),
            func.count(Problem.id).label("count"),
        )
        .filter(
            Problem.city        == city,
            Problem.status      == ProblemStatus.solved,
            Problem.change_reason.like("status_update%"),
            Problem.created_at  >= since,
        )
        .group_by(func.date(Problem.created_at))
        .all()
    )

    # Голоса по дням
    votes_by_day = (
        db.query(
            func.date(Vote.created_at).label("date"),
            func.count(Vote.id).label("count"),
        )
        .filter(Vote.created_at >= since, Vote.version == 1)
        .group_by(func.date(Vote.created_at))
        .all()
    )

    # Комментарии по дням
    comments_by_day = (
        db.query(
            func.date(Comment.created_at).label("date"),
            func.count(Comment.id).label("count"),
        )
        .filter(Comment.created_at >= since, Comment.version == 1)
        .group_by(func.date(Comment.created_at))
        .all()
    )

    # Собираем в словари для быстрого доступа
    new_map      = {str(r.date): r.count for r in new_by_day}
    solved_map   = {str(r.date): r.count for r in solved_by_day}
    votes_map    = {str(r.date): r.count for r in votes_by_day}
    comments_map = {str(r.date): r.count for r in comments_by_day}

    # Генерируем все дни периода — даже если данных нет
    result = []
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days - i - 1)).date()
        key  = str(date)
        result.append(PeriodStats(
            date           = key,
            new_problems   = new_map.get(key,      0),
            solved         = solved_map.get(key,   0),
            total_votes    = votes_map.get(key,    0),
            total_comments = comments_map.get(key, 0),
        ))

    return result


# ── Digital Twin аналитика ────────────────────────────────

def get_heatmap(
    db:   Session,
    city: str,
) -> list[HeatmapPoint]:
    """
    Данные тепловой карты — координаты всех активных проблем
    с весом = priority_score.
    Фронт (Leaflet / MapboxGL) рисует heatmap из этих точек.
    """
    rows = (
        db.query(
            ST_Y(Problem.location).label("lat"),   # latitude
            ST_X(Problem.location).label("lon"),   # longitude
            Problem.priority_score,
        )
        .filter(
            Problem.city       == city,
            Problem.is_current,
            Problem.status.in_([ProblemStatus.open, ProblemStatus.in_progress]),
            Problem.location is not None,
        )
        .all()
    )

    return [
        HeatmapPoint(
            latitude      = round(float(row.lat), 6),
            longitude     = round(float(row.lon), 6),
            weight        = round(float(row.priority_score), 4),
            problem_count = 1,
            avg_priority  = round(float(row.priority_score), 4),
        )
        for row in rows
    ]


def get_zone_indexes(
    db:   Session,
    city: str,
) -> list[ZoneIndexes]:
    """
    Индексы всех зон города для Digital Twin карты.
    Окрашивает районы по уровню риска/загрязнения/трафика.
    """
    zones = (
        db.query(Zone)
        .filter_by(city=city, is_current=True)
        .all()
    )

    result = []
    for zone in zones:
        total  = zone.total_problems
        solved = zone.solved_problems
        solve_rate = solved / total if total > 0 else 0.0

        result.append(ZoneIndexes(
            zone_entity_id  = zone.entity_id,
            zone_name       = zone.name,
            zone_type       = zone.zone_type,
            center_lat      = zone.center_lat,
            center_lon      = zone.center_lon,
            pollution_index = zone.pollution_index,
            traffic_index   = zone.traffic_index,
            risk_score      = zone.risk_score,
            open_problems   = zone.open_problems,
            solve_rate      = round(solve_rate, 4),
        ))

    return sorted(result, key=lambda z: z.risk_score, reverse=True)


def get_response_time_stats(
    db:   Session,
    city: str,
) -> ResponseTimeStats:
    """
    Время реакции властей/волонтёров.
    Считает разницу между версиями проблемы.

    Ищем пары версий:
    - version с change_reason='status_update_to_in_progress' → время начала
    - version с change_reason='status_update_to_solved'      → время решения
    """

    # Все решённые проблемы города
    solved_versions = (
        db.query(Problem)
        .filter(
            Problem.city   == city,
            Problem.status == ProblemStatus.solved,
            Problem.change_reason.in_([
                "status_update_to_solved",
                f"status_update_to_{ProblemStatus.solved.value}",
                f"status_update_to_{ProblemStatus.solved}",
            ]),
        )
        .all()
    )

    if not solved_versions:
        return ResponseTimeStats(
            avg_days_to_start  = 0.0,
            avg_days_to_solve  = 0.0,
            fastest_solve_days = 0.0,
            slowest_solve_days = 0.0,
            total_solved       = 0,
        )

    days_to_solve_list = []

    for solved_v in solved_versions:
        # Найти первую версию этой проблемы (version=1 = момент создания)
        first_v = (
            db.query(Problem)
            .filter_by(entity_id=solved_v.entity_id, version=1)
            .first()
        )
        if first_v and solved_v.created_at and first_v.created_at:
            delta = (solved_v.created_at - first_v.created_at).total_seconds()
            days  = delta / 86400  # секунды → дни
            days_to_solve_list.append(days)

    if not days_to_solve_list:
        return ResponseTimeStats(
            avg_days_to_start  = 0.0,
            avg_days_to_solve  = 0.0,
            fastest_solve_days = 0.0,
            slowest_solve_days = 0.0,
            total_solved       = len(solved_versions),
        )

    return ResponseTimeStats(
        avg_days_to_start  = 0.0,  # можно добавить аналогично для in_progress
        avg_days_to_solve  = round(sum(days_to_solve_list) / len(days_to_solve_list), 2),
        fastest_solve_days = round(min(days_to_solve_list), 2),
        slowest_solve_days = round(max(days_to_solve_list), 2),
        total_solved       = len(solved_versions),
    )


def get_city_digital_twin(db: Session, city: str) -> CityDigitalTwin:
    """
    Собирает полный Digital Twin срез города.
    Вызывается для главного дашборда.
    """
    return CityDigitalTwin(
        city          = city,
        snapshot_at   = datetime.now(timezone.utc),
        overview      = get_city_overview(db, city),
        zone_indexes  = get_zone_indexes(db, city),
        heatmap       = get_heatmap(db, city),
        response_time = get_response_time_stats(db, city),
        period_trend  = get_period_trend(db, city, days=30),
    )