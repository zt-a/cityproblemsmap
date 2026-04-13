# app/services/scoring.py
from sqlalchemy.orm import Session
from app.models.vote import Vote
from app.models.problem import Problem
from app.services.versioning import create_new_version


def recalculate_scores(
    db:                Session,
    problem_entity_id: int,
    changed_by_id:     int,
) -> Problem:
    """
    Пересчитывает все *_score для проблемы на основе текущих голосов.

    Использует взвешенное среднее — голос пользователя с высокой
    репутацией (weight=2.5) влияет больше чем новичка (weight=1.0).

    Вызывается после каждого нового голоса или изменения голоса.
    Создаёт новую версию проблемы с обновлёнными scores.
    """

    # Берём только актуальные голоса
    votes = (
        db.query(Vote)
        .filter_by(problem_entity_id=problem_entity_id, is_current=True)
        .all()
    )

    if not votes:
        return _get_current_problem(db, problem_entity_id)

    total_weight = sum(v.weight for v in votes)  # noqa: F841

    # ── Truth score ──────────────────────────────────────────
    # Только те кто проголосовал за правдивость (не воздержался)
    truth_votes = [v for v in votes if v.is_true is not None]
    if truth_votes:
        truth_weight = sum(v.weight for v in truth_votes)
        # Взвешенная доля голосов "правда"
        truth_score = sum(
            v.weight for v in truth_votes if v.is_true
        ) / truth_weight
    else:
        truth_score = 0.0

    # ── Urgency score ─────────────────────────────────────────
    urgency_score = _weighted_avg(votes, "urgency", max_val=5)

    # ── Impact score ──────────────────────────────────────────
    impact_score = _weighted_avg(votes, "impact", max_val=5)

    # ── Inconvenience score ───────────────────────────────────
    inconvenience_score = _weighted_avg(votes, "inconvenience", max_val=5)

    # ── Priority score ────────────────────────────────────────
    # Комплексная оценка: правдивость важнее всего
    # Если проблема оказалась фейком (truth_score < 0.3) — приоритет низкий
    priority_score = (
        truth_score       * 0.35 +
        urgency_score     * 0.30 +
        impact_score      * 0.25 +
        inconvenience_score * 0.10
    )

    # Создать новую версию проблемы с обновлёнными scores
    updated = create_new_version(
        db                  = db,
        model_class         = Problem,
        entity_id           = problem_entity_id,
        changed_by_id       = changed_by_id,
        change_reason       = "scores_recalculated",
        truth_score         = round(truth_score, 4),
        urgency_score       = round(urgency_score, 4),
        impact_score        = round(impact_score, 4),
        inconvenience_score = round(inconvenience_score, 4),
        priority_score      = round(priority_score, 4),
        vote_count          = len(votes),
    )
    return updated


def _weighted_avg(votes: list, field: str, max_val: int) -> float:
    """
    Взвешенное среднее по полю, нормализованное к 0.0–1.0.
    Пропускает голоса где поле не заполнено (None).
    """
    relevant = [(getattr(v, field), v.weight) for v in votes if getattr(v, field) is not None]
    if not relevant:
        return 0.0

    total_weight = sum(w for _, w in relevant)
    weighted_sum = sum(val * w for val, w in relevant)

    # Нормализация: делим на max_val чтобы получить 0.0–1.0
    return (weighted_sum / total_weight) / max_val


def _get_current_problem(db: Session, problem_entity_id: int) -> Problem:
    return (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .one()
    )