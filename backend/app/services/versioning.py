# app/services/versioning.py
from datetime import datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
# from app.models.mixins import VersionMixin


def create_new_version(
    db: Session,
    model_class: type,
    entity_id: int,
    changed_by_id: int | None,
    change_reason: str,
    **new_fields
):
    """
    Единственный способ изменить любую сущность в системе.

    1. Находит текущую версию
    2. Копирует все поля
    3. Применяет new_fields поверх
    4. INSERT новой версии
    5. Помечает старую is_current=False  ← единственный UPDATE

    Args:
        db: Database session
        model_class: Класс модели (например, Problem, User)
        entity_id: ID сущности
        changed_by_id: ID пользователя, который вносит изменения
        change_reason: Причина изменения для audit trail
        **new_fields: Поля для обновления

    Returns:
        Новая версия объекта

    Example:
        >>> updated_problem = create_new_version(
        ...     db=db,
        ...     model_class=Problem,
        ...     entity_id=123,
        ...     changed_by_id=user.entity_id,
        ...     change_reason="status_changed",
        ...     status="solved"
        ... )
    """

    # Найти текущую версию
    current = (
        db.query(model_class)
        .filter_by(entity_id=entity_id, is_current=True)
        .one()
    )

    # Получить все колонки модели через SQLAlchemy inspector
    mapper = inspect(model_class)
    column_names = [col.key for col in mapper.columns]

    # Скопировать все поля кроме служебных версионирования
    skip = {"id", "is_current", "created_at", "superseded_at"}
    data = {
        col: getattr(current, col)
        for col in column_names
        if col not in skip
    }

    # Применить изменения поверх скопированных полей
    data.update(new_fields)

    # Увеличить версию
    data["version"]       = current.version + 1
    data["is_current"]    = True
    data["change_reason"] = change_reason
    data["changed_by_id"] = changed_by_id

    # INSERT новой версии
    new_row = model_class(**data)
    db.add(new_row)

    # Единственный UPDATE в системе
    current.is_current    = False
    current.superseded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(new_row)
    return new_row


def read_current(
    db: Session,
    model_class: type,
    entity_id: int
) -> Optional[Any]:
    """
    Получить текущую версию сущности по entity_id.

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности

    Returns:
        Текущая версия объекта или None если не найдена

    Example:
        >>> problem = read_current(db, Problem, 123)
        >>> if problem:
        ...     print(problem.title)
    """
    return (
        db.query(model_class)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )


def read_all_current(
    db: Session,
    model_class: type,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[Any] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Any]:
    """
    Получить все текущие версии с фильтрами и пагинацией.

    Args:
        db: Database session
        model_class: Класс модели
        filters: Словарь фильтров (например, {"city": "Bishkek"})
        order_by: Поле для сортировки (например, Problem.created_at.desc())
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Список текущих версий объектов

    Example:
        >>> problems = read_all_current(
        ...     db=db,
        ...     model_class=Problem,
        ...     filters={"city": "Bishkek", "status": "open"},
        ...     order_by=Problem.priority_score.desc(),
        ...     limit=20,
        ...     offset=0
        ... )
    """
    query = db.query(model_class).filter_by(is_current=True)

    # Применить дополнительные фильтры
    if filters:
        query = query.filter_by(**filters)

    # Сортировка
    if order_by is not None:
        query = query.order_by(order_by)

    # Пагинация
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return query.all()


def soft_delete(
    db: Session,
    model_class: type,
    entity_id: int,
    deleted_by_id: int,
    reason: str = "deleted"
) -> bool:
    """
    Мягкое удаление сущности через is_current=False.

    Не создает новую версию, просто помечает текущую как неактуальную.
    Используется для сущностей, которые не требуют полной истории удалений
    (например, подписки, уведомления).

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности
        deleted_by_id: ID пользователя, который удаляет
        reason: Причина удаления

    Returns:
        True если удаление успешно, False если объект не найден

    Example:
        >>> success = soft_delete(
        ...     db=db,
        ...     model_class=Subscription,
        ...     entity_id=456,
        ...     deleted_by_id=user.entity_id,
        ...     reason="user_unsubscribed"
        ... )
    """
    current = (
        db.query(model_class)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not current:
        return False

    # Единственный допустимый UPDATE - пометка как неактуальной
    current.is_current = False
    current.superseded_at = datetime.now(timezone.utc)

    # Если модель поддерживает changed_by_id, обновляем
    if hasattr(current, 'changed_by_id'):
        current.changed_by_id = deleted_by_id
    if hasattr(current, 'change_reason'):
        current.change_reason = reason

    db.commit()
    return True


def read_history(
    db: Session,
    model_class: type,
    entity_id: int,
    order_by_version: bool = True
) -> List[Any]:
    """
    Получить все версии сущности (полную историю изменений).

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности
        order_by_version: Сортировать по версии (True) или по created_at (False)

    Returns:
        Список всех версий объекта от старой к новой

    Example:
        >>> history = read_history(db, Problem, 123)
        >>> for version in history:
        ...     print(f"v{version.version}: {version.status} at {version.created_at}")
    """
    query = db.query(model_class).filter_by(entity_id=entity_id)

    if order_by_version:
        query = query.order_by(model_class.version.asc())
    else:
        query = query.order_by(model_class.created_at.asc())

    return query.all()


def count_current(
    db: Session,
    model_class: type,
    filters: Optional[Dict[str, Any]] = None
) -> int:
    """
    Подсчитать количество текущих версий с фильтрами.

    Args:
        db: Database session
        model_class: Класс модели
        filters: Словарь фильтров

    Returns:
        Количество записей

    Example:
        >>> total = count_current(
        ...     db=db,
        ...     model_class=Problem,
        ...     filters={"city": "Bishkek", "status": "open"}
        ... )
    """
    query = db.query(model_class).filter_by(is_current=True)

    if filters:
        query = query.filter_by(**filters)

    return query.count()


def get_version(
    db: Session,
    model_class: type,
    entity_id: int,
    version: int
) -> Optional[Any]:
    """
    Получить конкретную версию сущности.

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности
        version: Номер версии

    Returns:
        Объект указанной версии или None

    Example:
        >>> old_version = get_version(db, Problem, 123, version=2)
        >>> if old_version:
        ...     print(f"Status in v2: {old_version.status}")
    """
    return (
        db.query(model_class)
        .filter_by(entity_id=entity_id, version=version)
        .first()
    )


def bulk_read_current(
    db: Session,
    model_class: type,
    entity_ids: List[int]
) -> List[Any]:
    """
    Получить несколько текущих версий по списку entity_id.

    Args:
        db: Database session
        model_class: Класс модели
        entity_ids: Список ID сущностей

    Returns:
        Список текущих версий объектов

    Example:
        >>> problems = bulk_read_current(db, Problem, [1, 2, 3, 4, 5])
        >>> for p in problems:
        ...     print(p.title)
    """
    if not entity_ids:
        return []

    return (
        db.query(model_class)
        .filter(
            model_class.entity_id.in_(entity_ids),
            model_class.is_current
        )
        .all()
    )


def exists_current(
    db: Session,
    model_class: type,
    entity_id: int
) -> bool:
    """
    Проверить существование текущей версии сущности.

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности

    Returns:
        True если существует, False иначе

    Example:
        >>> if exists_current(db, Problem, 123):
        ...     print("Problem exists")
    """
    return (
        db.query(model_class.id)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    ) is not None


def find_one_current(
    db: Session,
    model_class: type,
    **filters
) -> Optional[Any]:
    """
    Найти одну текущую версию по фильтрам.

    Args:
        db: Database session
        model_class: Класс модели
        **filters: Фильтры для поиска

    Returns:
        Первый найденный объект или None

    Example:
        >>> user = find_one_current(db, User, email="user@example.com")
        >>> if user:
        ...     print(user.username)
    """
    return (
        db.query(model_class)
        .filter_by(is_current=True, **filters)
        .first()
    )


def bulk_soft_delete(
    db: Session,
    model_class: type,
    entity_ids: List[int],
    deleted_by_id: int,
    reason: str = "bulk_deleted"
) -> int:
    """
    Мягкое удаление нескольких сущностей.

    Args:
        db: Database session
        model_class: Класс модели
        entity_ids: Список ID сущностей для удаления
        deleted_by_id: ID пользователя, который удаляет
        reason: Причина удаления

    Returns:
        Количество удаленных записей

    Example:
        >>> deleted_count = bulk_soft_delete(
        ...     db=db,
        ...     model_class=Notification,
        ...     entity_ids=[1, 2, 3, 4, 5],
        ...     deleted_by_id=user.entity_id,
        ...     reason="bulk_cleanup"
        ... )
    """
    if not entity_ids:
        return 0

    records = (
        db.query(model_class)
        .filter(
            model_class.entity_id.in_(entity_ids),
            model_class.is_current
        )
        .all()
    )

    count = 0
    for record in records:
        record.is_current = False
        record.superseded_at = datetime.now(timezone.utc)
        if hasattr(record, 'changed_by_id'):
            record.changed_by_id = deleted_by_id
        if hasattr(record, 'change_reason'):
            record.change_reason = reason
        count += 1

    db.commit()
    return count


def get_latest_version_number(
    db: Session,
    model_class: type,
    entity_id: int
) -> int:
    """
    Получить номер последней версии сущности.

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности

    Returns:
        Номер последней версии или 0 если не найдено

    Example:
        >>> latest = get_latest_version_number(db, Problem, 123)
        >>> print(f"Latest version: {latest}")
    """
    result = (
        db.query(model_class.version)
        .filter_by(entity_id=entity_id)
        .order_by(model_class.version.desc())
        .first()
    )
    return result[0] if result else 0


def restore_soft_deleted(
    db: Session,
    model_class: type,
    entity_id: int,
    restored_by_id: int,
    reason: str = "restored"
) -> Optional[Any]:
    """
    Восстановить мягко удаленную сущность.

    Args:
        db: Database session
        model_class: Класс модели
        entity_id: ID сущности
        restored_by_id: ID пользователя, который восстанавливает
        reason: Причина восстановления

    Returns:
        Восстановленный объект или None

    Example:
        >>> restored = restore_soft_deleted(
        ...     db=db,
        ...     model_class=Subscription,
        ...     entity_id=456,
        ...     restored_by_id=user.entity_id,
        ...     reason="user_resubscribed"
        ... )
    """
    # Найти последнюю версию (даже если is_current=False)
    last_version = (
        db.query(model_class)
        .filter_by(entity_id=entity_id)
        .order_by(model_class.version.desc())
        .first()
    )

    if not last_version:
        return None

    # Если уже активна, ничего не делаем
    if last_version.is_current:
        return last_version

    # Восстанавливаем через создание новой версии
    mapper = inspect(model_class)
    column_names = [col.key for col in mapper.columns]
    skip = {"id", "is_current", "created_at", "superseded_at"}

    data = {
        col: getattr(last_version, col)
        for col in column_names
        if col not in skip
    }

    data["version"] = last_version.version + 1
    data["is_current"] = True
    data["change_reason"] = reason
    data["changed_by_id"] = restored_by_id

    new_row = model_class(**data)
    db.add(new_row)
    db.commit()
    db.refresh(new_row)

    return new_row


def read_geospatial(
    db: Session,
    model_class: type,
    filters: Optional[Dict[str, Any]] = None,
    geospatial_filters: Optional[List[Any]] = None,
    order_by: Optional[Any] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Any]:
    """
    Получить текущие версии с геопространственными фильтрами (PostGIS).

    Специальный метод для запросов с ST_DWithin, ST_Distance и другими PostGIS функциями.

    Args:
        db: Database session
        model_class: Класс модели
        filters: Обычные фильтры (например, {"city": "Bishkek"})
        geospatial_filters: Список PostGIS фильтров (например, [ST_DWithin(...)])
        order_by: Поле для сортировки
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Список текущих версий объектов

    Example:
        >>> from geoalchemy2.functions import ST_DWithin, ST_MakePoint
        >>> point = ST_MakePoint(74.5698, 42.8746)
        >>> problems = read_geospatial(
        ...     db=db,
        ...     model_class=Problem,
        ...     filters={"problem_type": "pothole", "status": "open"},
        ...     geospatial_filters=[ST_DWithin(Problem.location, point, 100, use_spheroid=True)],
        ...     order_by=func.ST_Distance(Problem.location, point),
        ...     limit=10
        ... )
    """
    query = db.query(model_class).filter(model_class.is_current)

    # Применить обычные фильтры
    if filters:
        for key, value in filters.items():
            query = query.filter(getattr(model_class, key) == value)

    # Применить геопространственные фильтры
    if geospatial_filters:
        for geo_filter in geospatial_filters:
            query = query.filter(geo_filter)

    # Сортировка
    if order_by is not None:
        query = query.order_by(order_by)

    # Пагинация
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return query.all()


def read_with_custom_filters(
    db: Session,
    model_class: type,
    custom_filters: List[Any],
    order_by: Optional[Any] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Any]:
    """
    Получить текущие версии с произвольными SQLAlchemy фильтрами.

    Используется для сложных запросов с and_, or_, in_, like и т.д.

    Args:
        db: Database session
        model_class: Класс модели
        custom_filters: Список SQLAlchemy фильтров
        order_by: Поле для сортировки
        limit: Максимальное количество записей
        offset: Смещение для пагинации

    Returns:
        Список текущих версий объектов

    Example:
        >>> from sqlalchemy import and_, or_
        >>> problems = read_with_custom_filters(
        ...     db=db,
        ...     model_class=Problem,
        ...     custom_filters=[
        ...         Problem.status.in_(['open', 'in_progress']),
        ...         or_(
        ...             Problem.priority_score > 0.8,
        ...             Problem.vote_count >= 10
        ...         )
        ...     ],
        ...     order_by=Problem.created_at.desc(),
        ...     limit=20
        ... )
    """
    query = db.query(model_class).filter(model_class.is_current)

    # Применить все кастомные фильтры
    for custom_filter in custom_filters:
        query = query.filter(custom_filter)

    # Сортировка
    if order_by is not None:
        query = query.order_by(order_by)

    # Пагинация
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return query.all()


def count_with_custom_filters(
    db: Session,
    model_class: type,
    custom_filters: Optional[List[Any]] = None
) -> int:
    """
    Подсчитать количество текущих версий с произвольными фильтрами.

    Args:
        db: Database session
        model_class: Класс модели
        custom_filters: Список SQLAlchemy фильтров

    Returns:
        Количество записей

    Example:
        >>> from sqlalchemy import and_
        >>> total = count_with_custom_filters(
        ...     db=db,
        ...     model_class=Problem,
        ...     custom_filters=[
        ...         Problem.status == 'open',
        ...         Problem.city == 'Bishkek'
        ...     ]
        ... )
    """
    query = db.query(model_class).filter(model_class.is_current)

    if custom_filters:
        for custom_filter in custom_filters:
            query = query.filter(custom_filter)

    return query.count()