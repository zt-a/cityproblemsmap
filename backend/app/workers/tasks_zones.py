# app/workers/tasks_zones.py
from app.workers.celery_app import celery_app
from app.database import SessionLocal


@celery_app.task(
    name = "app.workers.tasks_zones.update_zone_stats",
    bind = True,
    max_retries = 3,
    default_retry_delay = 15,
)
def update_zone_stats(self, zone_entity_id: int, changed_by_id: int):
    """
    Пересчитывает статистику одной зоны.

    Запускается после:
    - создания проблемы в зоне
    - смены статуса проблемы

    Из problems роутера:
        update_zone_stats.delay(zone_entity_id, user_entity_id)
    """
    db = SessionLocal()
    try:
        from app.services.zones import recalculate_zone_stats
        from app.services.cache import invalidate_zone_cache

        recalculate_zone_stats(
            db             = db,
            zone_entity_id = zone_entity_id,
            changed_by_id  = changed_by_id,
        )

        # Инвалидируем кеш зоны после обновления статистики
        invalidate_zone_cache(zone_entity_id)

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks_zones.recalculate_all_zones")
def recalculate_all_zones():
    """
    Периодически пересчитывает статистику ВСЕХ зон.
    Запускается каждые 10 минут через Celery Beat.

    Нужен как страховка — на случай если update_zone_stats
    не сработал из-за ошибки или race condition.
    """
    db = SessionLocal()
    try:
        from app.models.zone import Zone
        from app.services.zones import recalculate_zone_stats
        from app.services.cache import CacheService

        zones = db.query(Zone).filter_by(is_current=True).all()

        for zone in zones:
            try:
                recalculate_zone_stats(
                    db             = db,
                    zone_entity_id = zone.entity_id,
                    changed_by_id  = 0,  # 0 = система
                )
                # Инвалидируем кеш зоны
                CacheService.delete_pattern(f"zone:*:{zone.entity_id}")
            except Exception:
                # Одна зона упала — не останавливаем остальные
                db.rollback()
                continue

        # Инвалидируем кеш списков зон
        CacheService.delete_pattern("zones:list:*")

    finally:
        db.close()