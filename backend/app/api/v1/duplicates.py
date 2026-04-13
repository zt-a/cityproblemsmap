# app/api/v1/duplicates.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.problem import ProblemType
from app.services.duplicates import check_for_duplicates_before_create

router = APIRouter(prefix="/duplicates", tags=["duplicates"])


@router.get("/check")
def check_duplicates(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    problem_type: ProblemType = Query(..., description="Тип проблемы"),
    title: str = Query(..., min_length=3, max_length=300, description="Заголовок проблемы"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Порог похожести (0.0-1.0)"),
    db: Session = Depends(get_db),
):
    """
    Проверить наличие дубликатов перед созданием проблемы.

    Использование:
    ```
    GET /api/v1/duplicates/check?lat=42.8746&lon=74.5698&problem_type=pothole&title=Яма на дороге
    ```

    Ответ:
    ```json
    {
      "has_duplicates": true,
      "duplicates": [
        {
          "entity_id": 123,
          "title": "Большая яма на дороге",
          "status": "open",
          "vote_count": 15,
          "similarity": 0.85,
          "distance_m": 45,
          "created_at": "2026-04-01T10:00:00",
          "url": "/problems/123"
        }
      ],
      "message": "Найдено 1 похожих проблем. Возможно, стоит проголосовать за существующую?"
    }
    ```
    """
    result = check_for_duplicates_before_create(
        db=db,
        lat=lat,
        lon=lon,
        problem_type=problem_type,
        title=title,
        threshold=threshold
    )

    return result
