# app/services/zones.py
from sqlalchemy.orm import Session
from app.models.zone import Zone
from app.models.problem import Problem, ProblemStatus, ProblemType
from app.services.versioning import create_new_version


def recalculate_zone_stats(
    db:             Session,
    zone_entity_id: int,
    changed_by_id:  int,
) -> Zone:
    """
    Пересчитывает статистику зоны на основе текущих проблем.
    Создаёт новую версию зоны — старая остаётся в БД.

    Вызывается Celery-задачей после:
    - создания новой проблемы в зоне
    - смены статуса проблемы
    """

    # Все текущие проблемы зоны
    problems = (
        db.query(Problem)
        .filter_by(zone_entity_id=zone_entity_id, is_current=True)
        .all()
    )

    total    = len(problems)
    open_    = sum(1 for p in problems if p.status == ProblemStatus.open)
    in_prog  = sum(1 for p in problems if p.status == ProblemStatus.in_progress)  # noqa: F841
    solved   = sum(1 for p in problems if p.status == ProblemStatus.solved)

    # pollution_index — средний impact_score проблем типа pollution
    pollution_problems = [
        p for p in problems
        if p.problem_type == ProblemType.pollution
        and p.status != ProblemStatus.rejected
    ]
    pollution_index = (
        sum(p.impact_score for p in pollution_problems) / len(pollution_problems)
        if pollution_problems else 0.0
    )

    # traffic_index — средний impact_score дорожных проблем
    traffic_types = {ProblemType.pothole, ProblemType.road_work, ProblemType.traffic_light}
    traffic_problems = [
        p for p in problems
        if p.problem_type in traffic_types
        and p.status != ProblemStatus.rejected
    ]
    traffic_index = (
        sum(p.impact_score for p in traffic_problems) / len(traffic_problems)
        if traffic_problems else 0.0
    )

    # risk_score — взвешенная комплексная оценка
    # Открытые проблемы с высоким priority_score повышают риск
    active_problems = [
        p for p in problems
        if p.status in (ProblemStatus.open, ProblemStatus.in_progress)
    ]
    risk_score = (
        sum(p.priority_score for p in active_problems) / len(active_problems)
        if active_problems else 0.0
    )

    updated = create_new_version(
        db              = db,
        model_class     = Zone,
        entity_id       = zone_entity_id,
        changed_by_id   = changed_by_id,
        change_reason   = "stats_recalculated",
        total_problems  = total,
        open_problems   = open_,
        solved_problems = solved,
        pollution_index = round(pollution_index, 4),
        traffic_index   = round(traffic_index, 4),
        risk_score      = round(risk_score, 4),
    )
    return updated


def get_zone_detailed_stats(
    db:             Session,
    zone_entity_id: int,
) -> dict:
    """
    Детальная статистика для Digital Twin дашборда.
    Считает распределение по типам проблем.
    """
    problems = (
        db.query(Problem)
        .filter_by(zone_entity_id=zone_entity_id, is_current=True)
        .all()
    )

    total    = len(problems)
    open_    = sum(1 for p in problems if p.status == ProblemStatus.open)
    solved   = sum(1 for p in problems if p.status == ProblemStatus.solved)
    rejected = sum(1 for p in problems if p.status == ProblemStatus.rejected)
    in_prog  = sum(1 for p in problems if p.status == ProblemStatus.in_progress)

    solve_rate = solved / total if total > 0 else 0.0

    # Топ типов проблем — сортируем по количеству
    type_counts: dict[str, int] = {}
    for p in problems:
        if p.status != ProblemStatus.rejected:
            key = p.problem_type.value
            type_counts[key] = type_counts.get(key, 0) + 1

    top_types = sorted(
        [{"type": k, "count": v} for k, v in type_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    return {
        "total_problems":    total,
        "open_problems":     open_,
        "solved_problems":   solved,
        "rejected_problems": rejected,
        "in_progress":       in_prog,
        "solve_rate":        round(solve_rate, 4),
        "top_problem_types": top_types,
    }