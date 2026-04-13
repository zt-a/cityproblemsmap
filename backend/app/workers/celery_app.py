# app/workers/celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "city_problems",
    broker  = settings.REDIS_URL,
    backend = settings.REDIS_URL,
)

celery_app.conf.update(
    # Сериализация — JSON безопаснее pickle
    task_serializer   = "json",
    result_serializer = "json",
    accept_content    = ["json"],

    # Timezone
    timezone          = "Asia/Bishkek",
    enable_utc        = True,

    # Если задача не выполнилась за 5 минут — убить
    task_time_limit   = 300,

    # Soft limit — за 4 минуты кинуть SoftTimeLimitExceeded
    task_soft_time_limit = 240,

    # Автоматически находим задачи в этих модулях
    include = [
        "app.workers.tasks_scoring",
        "app.workers.tasks_zones",
        "app.workers.tasks_maintenance",
    ],
)

# ── Расписание периодических задач (Celery Beat) ──────────
celery_app.conf.beat_schedule = {

    # Каждые 10 минут — пересчёт статистики зон
    "recalculate-zone-stats": {
        "task":     "app.workers.tasks_zones.recalculate_all_zones",
        "schedule": crontab(minute="*/10"),
    },

    # Каждый день в 03:00 — архивирование старых проблем
    "archive-stale-problems": {
        "task":     "app.workers.tasks_maintenance.archive_stale_problems",
        "schedule": crontab(hour=3, minute=0),
    },

    # Каждый день в 03:30 — автоотклонение фейков
    "auto-reject-fakes": {
        "task":     "app.workers.tasks_maintenance.auto_reject_fake_problems",
        "schedule": crontab(hour=3, minute=30),
    },

    # Каждый день в 04:00 — decay репутации
    "decay-reputation": {
        "task":     "app.workers.tasks_maintenance.decay_reputation",
        "schedule": crontab(hour=4, minute=0),
    },
}