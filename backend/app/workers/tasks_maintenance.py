# app/workers/tasks_maintenance.py
from datetime import datetime, timedelta, timezone
from app.workers.celery_app import celery_app
from app.database import SessionLocal


@celery_app.task(name="app.workers.tasks_maintenance.archive_stale_problems")
def archive_stale_problems():
    """
    Архивирует открытые проблемы без активности > 180 дней.

    Проблема считается неактивной если:
    - статус open или in_progress
    - последняя версия создана > 180 дней назад
    - нет новых голосов или комментариев за этот период

    Создаёт новую версию с status=archived — данные не удаляются.
    """
    db = SessionLocal()
    try:
        from app.models.problem import Problem, ProblemStatus
        from app.services.versioning import create_new_version

        cutoff = datetime.now(timezone.utc) - timedelta(days=180)

        stale = (
            db.query(Problem)
            .filter(
                Problem.is_current,
                Problem.status.in_([
                    ProblemStatus.open,
                    ProblemStatus.in_progress,
                ]),
                Problem.created_at <= cutoff,
            )
            .all()
        )

        archived_count = 0
        for problem in stale:
            try:
                create_new_version(
                    db            = db,
                    model_class   = Problem,
                    entity_id     = problem.entity_id,
                    changed_by_id = 0,   # 0 = система
                    change_reason = "auto_archived_stale",
                    status        = ProblemStatus.archived,
                )
                archived_count += 1
            except Exception:
                db.rollback()
                continue

        return {"archived": archived_count}

    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_maintenance.auto_reject_fake_problems")
def auto_reject_fake_problems():
    """
    Автоматически отклоняет проблемы которые сообщество
    признало фейком.

    Условия для автоотклонения (все три):
    - truth_score < 0.2  (80%+ голосов считают фейком)
    - vote_count >= 5    (достаточно голосов для решения)
    - статус open        (ещё не обработана)

    Создаёт новую версию с status=rejected.
    Начисляет штраф репутации автору.
    """
    db = SessionLocal()
    try:
        from app.models.problem import Problem, ProblemStatus
        from app.models.reputation import ReputationLog
        from app.services.versioning import create_new_version

        fakes = (
            db.query(Problem)
            .filter(
                Problem.is_current,
                Problem.status      == ProblemStatus.open,
                Problem.truth_score <  0.2,
                Problem.vote_count  >= 5,
            )
            .all()
        )

        rejected_count = 0
        for problem in fakes:
            try:
                # Новая версия проблемы — rejected
                create_new_version(
                    db            = db,
                    model_class   = Problem,
                    entity_id     = problem.entity_id,
                    changed_by_id = 0,
                    change_reason = "auto_rejected_low_truth_score",
                    status        = ProblemStatus.rejected,
                )

                # Штраф репутации автору
                author = (
                    db.query(
                        __import__("app.models.user", fromlist=["User"]).User
                    )
                    .filter_by(
                        entity_id  = problem.author_entity_id,
                        is_current = True,
                    )
                    .first()
                )

                if author:
                    penalty = -1.0
                    log = ReputationLog(
                        user_entity_id              = author.entity_id,
                        delta                       = penalty,
                        reason                      = "false_report_penalty",
                        note                        = f"Проблема #{problem.entity_id} отклонена как фейк",
                        related_problem_entity_id   = problem.entity_id,
                        snapshot_reputation         = author.reputation + penalty,
                    )
                    db.add(log)

                    # Обновляем репутацию через новую версию юзера
                    from app.services.versioning import create_new_version as cnv
                    from app.models.user import User
                    cnv(
                        db            = db,
                        model_class   = User,
                        entity_id     = author.entity_id,
                        changed_by_id = 0,
                        change_reason = "reputation_penalty_false_report",
                        reputation    = max(0.0, author.reputation + penalty),
                    )

                db.commit()
                rejected_count += 1

            except Exception:
                db.rollback()
                continue

        return {"rejected": rejected_count}

    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_maintenance.decay_reputation")
def decay_reputation():
    """
    Небольшое снижение репутации неактивных пользователей.
    Запускается раз в день.

    Логика:
    - Пользователи без активности > 90 дней теряют 0.1 репутации
    - Минимум репутации = 0.0 (не уходит в минус)
    - Верифицированные пользователи не подвержены decay

    Это мотивирует пользователей быть активными
    и сохраняет качество голосов в системе.
    """
    db = SessionLocal()
    try:
        from app.models.user import User, UserStatus
        from app.models.reputation import ReputationLog
        from app.services.versioning import create_new_version

        cutoff = datetime.now(timezone.utc) - timedelta(days=90)

        # Неактивные пользователи с ненулевой репутацией
        inactive = (
            db.query(User)
            .filter(
                User.is_current,
                User.status        == UserStatus.active,
                not User.is_verified,   # верифицированных не трогаем
                User.reputation    >  0.0,
                User.created_at    <= cutoff,
            )
            .all()
        )

        decayed_count = 0
        for user in inactive:
            try:
                decay   = 0.1
                new_rep = max(0.0, round(user.reputation - decay, 4))

                if new_rep == user.reputation:
                    continue  # уже 0.0 — пропускаем

                log = ReputationLog(
                    user_entity_id      = user.entity_id,
                    delta               = -decay,
                    reason              = "inactivity_decay",
                    note                = "Снижение репутации за неактивность",
                    snapshot_reputation = new_rep,
                )
                db.add(log)

                create_new_version(
                    db            = db,
                    model_class   = User,
                    entity_id     = user.entity_id,
                    changed_by_id = 0,
                    change_reason = "reputation_decay",
                    reputation    = new_rep,
                )
                decayed_count += 1

            except Exception:
                db.rollback()
                continue

        return {"decayed": decayed_count}

    finally:
        db.close()