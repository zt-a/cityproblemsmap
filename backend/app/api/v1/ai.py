# app/api/v1/ai.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from app.database import get_db
from app.models.problem import Problem
from app.schemas.ai import DuplicatesList, DuplicateResult, FindDuplicatesRequest
from app.services.ai_duplicates import DuplicateDetector
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/ai", tags=["ai"])


def _problem_to_public(problem: Problem):
    """Конвертировать Problem в ProblemPublic"""
    from app.api.v1.problems import _to_public
    return _to_public(problem)


@router.get("/similar-problems/{entity_id}", response_model=DuplicatesList)
def get_similar_problems(
    entity_id: int,
    method: str = Query("combined", description="Метод: text/location/combined"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Найти похожие проблемы для существующей проблемы.

    Методы:
    - text: Только текстовое сходство (TF-IDF)
    - location: Только геолокация (в радиусе 500м)
    - combined: Комбинация текста и геолокации (рекомендуется)
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )

    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    detector = DuplicateDetector(similarity_threshold=0.5)

    if method == "text":
        results = detector.find_duplicates(db, problem, city=problem.city, limit=limit)
    elif method == "location":
        results = detector.find_similar_by_location(db, problem, radius_meters=500, limit=limit)
    elif method == "combined":
        results = detector.find_combined_duplicates(db, problem, limit=limit)
    else:
        raise HTTPException(status_code=400, detail="Неверный метод")

    items = [
        DuplicateResult(
            problem=_problem_to_public(prob),
            similarity_score=score,
        )
        for prob, score in results
    ]

    return DuplicatesList(
        items=items,
        total=len(items),
    )


@router.post("/find-duplicates", response_model=DuplicatesList)
def find_duplicates_before_create(
    data: FindDuplicatesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Найти дубликаты перед созданием проблемы.
    Используется на фронтенде для предупреждения пользователя.

    Создает временную проблему в памяти (не сохраняет в БД)
    и ищет похожие существующие проблемы.
    """
    # Создаем временную проблему для поиска
    temp_problem = Problem(
        entity_id=0,  # Временный ID
        version=1,
        is_current=True,
        author_entity_id=current_user.entity_id,
        title=data.title,
        description=data.description,
        city=data.city,
        problem_type=data.problem_type,
        tags=data.tags,
    )

    # Добавляем геолокацию если есть
    if data.latitude and data.longitude:
        temp_problem.location = ST_SetSRID(
            ST_MakePoint(data.longitude, data.latitude), 4326
        )

    detector = DuplicateDetector(similarity_threshold=0.6)

    # Используем комбинированный метод если есть координаты
    if data.latitude and data.longitude:
        results = detector.find_combined_duplicates(db, temp_problem, limit=10)
    else:
        results = detector.find_duplicates(db, temp_problem, city=data.city, limit=10)

    items = [
        DuplicateResult(
            problem=_problem_to_public(prob),
            similarity_score=score,
        )
        for prob, score in results
    ]

    return DuplicatesList(
        items=items,
        total=len(items),
    )


@router.get("/duplicates-stats")
def get_duplicates_stats(
    city: str = Query(..., description="Город для анализа"),
    threshold: float = Query(0.8, ge=0, le=1, description="Порог сходства"),
    db: Session = Depends(get_db),
):
    """
    Статистика потенциальных дубликатов в городе.
    Полезно для модераторов для очистки базы.
    """
    # Получаем все проблемы города
    problems = (
        db.query(Problem)
        .filter_by(city=city, is_current=True)
        .limit(1000)  # Ограничиваем для производительности
        .all()
    )

    if not problems:
        return {
            "city": city,
            "total_problems": 0,
            "potential_duplicates": 0,
            "duplicate_groups": [],
        }

    detector = DuplicateDetector(similarity_threshold=threshold)

    # Находим группы дубликатов
    duplicate_groups = []
    processed = set()

    for problem in problems:
        if problem.entity_id in processed:
            continue

        duplicates = detector.find_duplicates(
            db, problem, city=city, limit=10
        )

        if duplicates:
            group = {
                "main_problem_id": problem.entity_id,
                "main_problem_title": problem.title,
                "duplicates": [
                    {
                        "problem_id": dup.entity_id,
                        "title": dup.title,
                        "similarity": score,
                    }
                    for dup, score in duplicates
                ],
            }
            duplicate_groups.append(group)

            # Помечаем как обработанные
            processed.add(problem.entity_id)
            for dup, _ in duplicates:
                processed.add(dup.entity_id)

    return {
        "city": city,
        "total_problems": len(problems),
        "potential_duplicates": len(processed),
        "duplicate_groups": duplicate_groups[:20],  # Топ 20 групп
    }
