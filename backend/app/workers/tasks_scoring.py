# app/workers/tasks_scoring.py
from app.workers.celery_app import celery_app
from app.database import SessionLocal


@celery_app.task(
    name    = "app.workers.tasks_scoring.recalculate_problem_scores",
    bind    = True,          # self = task instance (для retry)
    max_retries = 3,
    default_retry_delay = 10,  # секунд между retry
)
def recalculate_problem_scores(self, problem_entity_id: int, changed_by_id: int):
    """
    Пересчитывает все *_score проблемы после нового голоса.

    Запускается из votes роутера:
        recalculate_problem_scores.delay(problem_entity_id, user_entity_id)

    Вместо синхронного вызова — не блокирует HTTP ответ пользователю.
    """
    db = SessionLocal()
    try:
        from app.services.scoring import recalculate_scores
        recalculate_scores(
            db                = db,
            problem_entity_id = problem_entity_id,
            changed_by_id     = changed_by_id,
        )
    except Exception as exc:
        db.rollback()
        # Повторить задачу через 10 секунд если упала
        raise self.retry(exc=exc)
    finally:
        db.close()