# app/services/analytics_extended.py
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models.problem import Problem, ProblemStatus
from app.models.zone import Zone
from app.models.user import User
from app.models.vote import Vote
from app.models.comment import Comment
from app.schemas.analytics_extended import (
    ZoneComparison,
    TopZone,
    UserLeaderboard,
    OfficialEfficiency,
    ProblemTrend,
)


def get_zones_comparison(
    db: Session,
    zone_ids: list[int],
) -> list[ZoneComparison]:
    """Сравнение нескольких зон"""
    zones = (
        db.query(Zone)
        .filter(
            Zone.entity_id.in_(zone_ids),
            Zone.is_current == True,
        )
        .all()
    )

    result = []
    for zone in zones:
        # Средний приоритет проблем в зоне
        avg_priority = (
            db.query(func.avg(Problem.priority_score))
            .filter(
                Problem.zone_entity_id == zone.entity_id,
                Problem.is_current == True,
            )
            .scalar()
        ) or 0.0

        # Среднее время решения
        solved_problems = (
            db.query(Problem)
            .filter(
                Problem.zone_entity_id == zone.entity_id,
                Problem.status == ProblemStatus.solved,
                Problem.change_reason.like("%status_update_to_solved%"),
            )
            .all()
        )

        response_times = []
        for solved in solved_problems:
            first_version = (
                db.query(Problem)
                .filter_by(entity_id=solved.entity_id, version=1)
                .first()
            )
            if first_version:
                delta = (solved.created_at - first_version.created_at).total_seconds()
                response_times.append(delta / 86400)

        avg_response = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        solve_rate = (
            zone.solved_problems / zone.total_problems
            if zone.total_problems > 0
            else 0.0
        )

        result.append(
            ZoneComparison(
                zone_id=zone.entity_id,
                zone_name=zone.name,
                total_problems=zone.total_problems,
                open_problems=zone.open_problems,
                solved_problems=zone.solved_problems,
                solve_rate=round(solve_rate, 4),
                avg_priority=round(float(avg_priority), 4),
                avg_response_days=round(avg_response, 2),
                pollution_index=zone.pollution_index,
                traffic_index=zone.traffic_index,
                risk_score=zone.risk_score,
            )
        )

    return result


def get_top_problematic_zones(
    db: Session,
    city: str,
    limit: int = 10,
) -> list[TopZone]:
    """Топ проблемных зон города"""
    zones = (
        db.query(Zone)
        .filter(
            Zone.city == city,
            Zone.is_current == True,
        )
        .order_by(desc(Zone.risk_score))
        .limit(limit)
        .all()
    )

    result = []
    for rank, zone in enumerate(zones, start=1):
        avg_priority = (
            db.query(func.avg(Problem.priority_score))
            .filter(
                Problem.zone_entity_id == zone.entity_id,
                Problem.is_current == True,
            )
            .scalar()
        ) or 0.0

        result.append(
            TopZone(
                zone_entity_id=zone.entity_id,
                zone_name=zone.name,
                zone_type=zone.zone_type,
                open_problems=zone.open_problems,
                risk_score=zone.risk_score,
                avg_priority=round(float(avg_priority), 4),
                rank=rank,
            )
        )

    return result


def get_user_leaderboard(
    db: Session,
    city: str,
    limit: int = 50,
    period_days: int = 30,
) -> list[UserLeaderboard]:
    """Рейтинг активных пользователей"""
    since = datetime.now(timezone.utc) - timedelta(days=period_days)

    # Подсчёт активности пользователей
    user_stats = (
        db.query(
            User.entity_id,
            User.username,
            User.reputation,
            func.count(Problem.id).label("problems_created"),
        )
        .outerjoin(
            Problem,
            and_(
                Problem.author_entity_id == User.entity_id,
                Problem.version == 1,
                Problem.created_at >= since,
            ),
        )
        .filter(
            User.is_current == True,
            User.city == city,
        )
        .group_by(User.entity_id, User.username, User.reputation)
        .order_by(desc(User.reputation))
        .limit(limit)
        .all()
    )

    result = []
    for rank, (user_id, username, reputation, problems_created) in enumerate(
        user_stats, start=1
    ):
        # Подсчёт комментариев
        comments_count = (
            db.query(func.count(Comment.id))
            .filter(
                Comment.author_entity_id == user_id,
                Comment.created_at >= since,
                Comment.version == 1,
            )
            .scalar()
        ) or 0

        # Подсчёт голосов
        votes_count = (
            db.query(func.count(Vote.id))
            .filter(
                Vote.user_entity_id == user_id,
                Vote.created_at >= since,
                Vote.version == 1,
            )
            .scalar()
        ) or 0

        result.append(
            UserLeaderboard(
                user_entity_id=user_id,
                username=username,
                problems_created=problems_created,
                problems_solved=0,  # TODO: добавить для волонтёров
                comments_count=comments_count,
                votes_count=votes_count,
                reputation=reputation,
                rank=rank,
            )
        )

    return result


def get_officials_efficiency(
    db: Session,
    city: str,
    limit: int = 20,
) -> list[OfficialEfficiency]:
    """Рейтинг эффективности официальных лиц"""
    # Получить всех официалов города
    officials = (
        db.query(User)
        .filter(
            User.city == city,
            User.role.in_(["official", "moderator"]),
            User.is_current == True,
        )
        .all()
    )

    result = []
    for official in officials:
        # Назначенные проблемы
        assigned = (
            db.query(Problem)
            .filter(
                Problem.assigned_to_entity_id == official.entity_id,
                Problem.is_current == True,
            )
            .all()
        )

        assigned_count = len(assigned)
        if assigned_count == 0:
            continue

        # Решённые проблемы
        solved = [p for p in assigned if p.status == ProblemStatus.solved]
        solved_count = len(solved)

        # Среднее время решения
        response_times = []
        for problem in solved:
            solved_version = (
                db.query(Problem)
                .filter(
                    Problem.entity_id == problem.entity_id,
                    Problem.status == ProblemStatus.solved,
                    Problem.change_reason.like("%status_update_to_solved%"),
                )
                .first()
            )

            first_version = (
                db.query(Problem)
                .filter_by(entity_id=problem.entity_id, version=1)
                .first()
            )

            if solved_version and first_version:
                delta = (
                    solved_version.created_at - first_version.created_at
                ).total_seconds()
                response_times.append(delta / 86400)

        avg_response = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )
        solve_rate = solved_count / assigned_count if assigned_count > 0 else 0.0

        result.append(
            OfficialEfficiency(
                user_entity_id=official.entity_id,
                username=official.username,
                assigned_problems=assigned_count,
                solved_problems=solved_count,
                avg_response_days=round(avg_response, 2),
                solve_rate=round(solve_rate, 4),
                rank=0,  # Будет установлен после сортировки
            )
        )

    # Сортировка по solve_rate и avg_response_days
    result.sort(key=lambda x: (-x.solve_rate, x.avg_response_days))

    # Установить ранги
    for rank, item in enumerate(result[:limit], start=1):
        item.rank = rank

    return result[:limit]


def get_problem_trends_by_type(
    db: Session,
    city: str,
    days: int = 30,
) -> list[ProblemTrend]:
    """Тренды по типам проблем"""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    trends = (
        db.query(
            Problem.problem_type,
            func.date(Problem.created_at).label("date"),
            func.count(Problem.id).label("count"),
            func.avg(Problem.priority_score).label("avg_priority"),
        )
        .filter(
            Problem.city == city,
            Problem.version == 1,
            Problem.created_at >= since,
        )
        .group_by(Problem.problem_type, func.date(Problem.created_at))
        .order_by(func.date(Problem.created_at))
        .all()
    )

    return [
        ProblemTrend(
            problem_type=trend.problem_type.value,
            date=str(trend.date),
            count=trend.count,
            avg_priority=round(float(trend.avg_priority or 0), 4),
        )
        for trend in trends
    ]
