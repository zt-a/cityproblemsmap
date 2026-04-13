# app/services/duplicates.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from geoalchemy2.shape import to_shape

from app.models.problem import Problem, ProblemType, ProblemStatus
from app.services.versioning import read_geospatial


def find_similar_problems(
    db: Session,
    lat: float,
    lon: float,
    problem_type: ProblemType,
    radius_m: int = 100,
    days: int = 7,
    exclude_entity_id: Optional[int] = None
) -> List[Problem]:
    """
    Найти похожие проблемы по геолокации и типу.

    Критерии:
    - Расстояние < radius_m метров
    - Тот же тип проблемы
    - Создано за последние days дней
    - Статус open или in_progress

    Args:
        db: Database session
        lat: Широта
        lon: Долгота
        problem_type: Тип проблемы
        radius_m: Радиус поиска в метрах (по умолчанию 100м)
        days: Количество дней назад (по умолчанию 7)
        exclude_entity_id: Исключить проблему с этим entity_id

    Returns:
        Список похожих проблем, отсортированных по расстоянию
    """
    # Создать точку для поиска с правильным SRID
    point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)

    # Дата отсечки
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Базовые фильтры
    filters = {
        "problem_type": problem_type
    }

    # Конвертировать метры в градусы (примерно 1 градус = 111 км)
    radius_degrees = radius_m / 111000.0

    # Геопространственные и дополнительные фильтры
    geospatial_filters = [
        ST_DWithin(Problem.location, point, radius_degrees),
        Problem.status.in_([ProblemStatus.open, ProblemStatus.in_progress]),
        Problem.created_at >= cutoff_date
    ]

    # Исключить текущую проблему если указано
    if exclude_entity_id:
        geospatial_filters.append(Problem.entity_id != exclude_entity_id)

    # Использовать метод из versioning.py для геопространственных запросов
    return read_geospatial(
        db=db,
        model_class=Problem,
        filters=filters,
        geospatial_filters=geospatial_filters,
        order_by=func.ST_Distance(Problem.location, point),
        limit=10
    )


def calculate_similarity_score(
    problem1: Problem,
    problem2: Problem,
    lat1: float = None,
    lon1: float = None
) -> float:
    """
    Рассчитать степень похожести двух проблем (0.0 - 1.0).

    Факторы:
    - Расстояние (чем ближе, тем выше)
    - Тип проблемы (совпадает = +0.3)
    - Похожесть заголовков (Levenshtein distance)
    - Временная близость

    Args:
        problem1: Первая проблема
        problem2: Вторая проблема
        lat1: Широта первой проблемы (если problem1.location отсутствует)
        lon1: Долгота первой проблемы (если problem1.location отсутствует)

    Returns:
        Оценка похожести от 0.0 до 1.0
    """
    score = 0.0

    # 1. Тип проблемы (30%)
    if problem1.problem_type == problem2.problem_type:
        score += 0.3

    # 2. Расстояние (40%)
    if lat1 is not None and lon1 is not None:
        # Используем переданные координаты
        point2 = to_shape(problem2.location)
        distance = ((lon1 - point2.x)**2 + (lat1 - point2.y)**2)**0.5 * 111000
    else:
        # Используем location из обоих объектов
        point1 = to_shape(problem1.location)
        point2 = to_shape(problem2.location)
        distance = ((point1.x - point2.x)**2 + (point1.y - point2.y)**2)**0.5 * 111000

    if distance < 50:
        score += 0.4
    elif distance < 100:
        score += 0.3
    elif distance < 200:
        score += 0.2
    elif distance < 500:
        score += 0.1

    # 3. Похожесть заголовков (20%)
    title_similarity = calculate_text_similarity(
        problem1.title.lower(),
        problem2.title.lower()
    )
    score += title_similarity * 0.2

    # 4. Временная близость (10%)
    # Обработка naive datetime для совместимости со старыми данными
    dt1 = problem1.created_at
    dt2 = problem2.created_at

    # Если один из datetime naive, делаем оба naive для сравнения
    if dt1.tzinfo is None and dt2.tzinfo is not None:
        dt2 = dt2.replace(tzinfo=None)
    elif dt1.tzinfo is not None and dt2.tzinfo is None:
        dt1 = dt1.replace(tzinfo=None)

    time_diff = abs((dt1 - dt2).total_seconds())
    if time_diff < 3600:  # < 1 час
        score += 0.1
    elif time_diff < 86400:  # < 1 день
        score += 0.05

    return min(score, 1.0)


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Рассчитать похожесть двух текстов (простой алгоритм).

    Использует Jaccard similarity на словах.

    Args:
        text1: Первый текст
        text2: Второй текст

    Returns:
        Оценка похожести от 0.0 до 1.0
    """
    if not text1 or not text2:
        return 0.0

    # Разбить на слова
    words1 = set(text1.split())
    words2 = set(text2.split())

    # Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    if union == 0:
        return 0.0

    return intersection / union


def check_for_duplicates_before_create(
    db: Session,
    lat: float,
    lon: float,
    problem_type: ProblemType,
    title: str,
    threshold: float = 0.7
) -> dict:
    """
    Проверить наличие дубликатов перед созданием проблемы.

    Args:
        db: Database session
        lat: Широта
        lon: Долгота
        problem_type: Тип проблемы
        title: Заголовок проблемы
        threshold: Порог похожести (по умолчанию 0.7)

    Returns:
        {
            'has_duplicates': bool,
            'duplicates': List[dict],
            'message': str
        }
    """
    # Найти похожие проблемы
    similar = find_similar_problems(
        db=db,
        lat=lat,
        lon=lon,
        problem_type=problem_type,
        radius_m=200,  # Увеличенный радиус для проверки
        days=30  # Проверяем за месяц
    )

    if not similar:
        return {
            'has_duplicates': False,
            'duplicates': [],
            'message': 'Похожих проблем не найдено'
        }

    # Создать временную проблему для сравнения
    temp_problem = Problem(
        title=title,
        problem_type=problem_type,
        created_at=datetime.now(timezone.utc)
    )

    # Рассчитать похожесть
    duplicates = []
    for problem in similar:
        similarity = calculate_similarity_score(temp_problem, problem, lat, lon)

        if similarity >= threshold:
            point = to_shape(problem.location)
            duplicates.append({
                'entity_id': problem.entity_id,
                'title': problem.title,
                'status': problem.status.value,
                'vote_count': problem.vote_count,
                'similarity': round(similarity, 2),
                'distance_m': round(
                    ((point.x - lon)**2 + (point.y - lat)**2)**0.5 * 111000,
                    0
                ),
                'created_at': problem.created_at.isoformat(),
                'url': f"/problems/{problem.entity_id}"
            })

    if duplicates:
        return {
            'has_duplicates': True,
            'duplicates': sorted(duplicates, key=lambda x: x['similarity'], reverse=True),
            'message': f'Найдено {len(duplicates)} похожих проблем. Возможно, стоит проголосовать за существующую?'
        }

    return {
        'has_duplicates': False,
        'duplicates': [],
        'message': 'Похожих проблем не найдено'
    }
