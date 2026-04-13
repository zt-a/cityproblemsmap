# app/services/geo.py
from fastapi import HTTPException, status
from app.models.user import User


def check_user_city(user: User, problem_city: str) -> None:
    """
    Пользователь может создавать проблемы только в своём городе.
    Если город не указан в профиле — разрешаем (пусть заполнит).
    """
    if not user.city:
        return

    if user.city.lower().strip() != problem_city.lower().strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Ты можешь добавлять проблемы только в своём городе ({user.city}). "
                f"Попытка добавить в: {problem_city}"
            ),
        )