# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth import decode_token, get_user_by_entity_id


# Читает токен из заголовка: Authorization: Bearer <token>
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency для защищённых эндпоинтов.
    Достаёт entity_id из токена, возвращает текущего пользователя.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный или просроченный токен",
    )

    # Если токен не предоставлен
    if credentials is None:
        raise credentials_error

    try:
        payload = decode_token(credentials.credentials)

        # Проверяем что это access токен, а не refresh
        if payload.get("type") != "access":
            raise credentials_error

        entity_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_error

    user = get_user_by_entity_id(db, entity_id)
    if not user or user.status != "active":
        raise credentials_error

    # Проверяем бан
    if user.is_banned:
        from datetime import datetime
        # Проверяем не истек ли временный бан
        if user.ban_until and user.ban_until <= datetime.now(timezone.utc):
            # Бан истек, но еще не обработан системой - пропускаем
            pass
        else:
            # Пользователь забанен
            ban_message = f"Аккаунт заблокирован. Причина: {user.ban_reason or 'Не указана'}"
            if user.ban_until:
                ban_message += f". До: {user.ban_until.isoformat()}"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ban_message,
            )

    return user


def require_role(*roles: UserRole):
    """
    Dependency-фабрика для проверки роли.

    Использование:
        @router.delete("/...", dependencies=[Depends(require_role(UserRole.admin))])
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user
    return checker


def get_moderator(
    current_user: User = Depends(
        require_role(UserRole.moderator, UserRole.official, UserRole.admin)
    )
) -> User:
    """Модератор, official или admin."""
    return current_user


def get_official(
    current_user: User = Depends(
        require_role(UserRole.official, UserRole.admin)
    )
) -> User:
    """Official или admin."""
    return current_user


def get_admin(
    current_user: User = Depends(require_role(UserRole.admin))
) -> User:
    """Только admin."""
    return current_user