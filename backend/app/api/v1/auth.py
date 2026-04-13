# app/api/v1/auth.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister, UserLogin, UserPublic,
    TokenResponse, RefreshRequest,
)
from app.schemas.auth import (
    ChangePasswordRequest, ForgotPasswordRequest,
    ResetPasswordRequest, LogoutRequest, MessageResponse,
)
from app.services.auth import (
    hash_password, verify_password, authenticate_user,
    create_access_token, create_refresh_token,
    decode_token, get_user_by_entity_id, get_user_by_email,
)
from app.services.versioning import create_new_version
from app.services.redis_client import (
    blacklist_token, is_token_blacklisted,
    save_reset_token, get_reset_token_entity_id, delete_reset_token,
)
from app.services.email import send_reset_password_email
from app.api.deps import get_current_user
from app.config import settings
from app.middleware.rate_limit import limiter
from app.dependencies.captcha import verify_captcha_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/hour")  # Максимум 5 регистраций в час с одного IP
def register(
    request: Request,
    data: UserRegister,
    db: Session = Depends(get_db),
    captcha_verified: bool = Depends(verify_captcha_token)
):
    """Регистрация нового пользователя."""
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")

    existing_username = (
        db.query(User)
        .filter_by(username=data.username, is_current=True)
        .first()
    )
    if existing_username:
        raise HTTPException(status_code=409, detail="Username уже занят")

    entity_id = User.next_entity_id(db)
    user      = User(
        entity_id       = entity_id,
        version         = 1,
        is_current      = True,
        username        = data.username,
        email           = data.email,
        hashed_password = hash_password(data.password),
        country         = data.country,
        city            = data.city,
        district        = data.district,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token  = create_access_token(entity_id),
        refresh_token = create_refresh_token(entity_id),
        user          = UserPublic.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")  # Защита от брутфорса - 10 попыток в минуту
def login(
    request: Request,
    data: UserLogin,
    db: Session = Depends(get_db),
    captcha_verified: bool = Depends(verify_captcha_token)
):
    """Логин по email + паролю."""
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
        )
    return TokenResponse(
        access_token  = create_access_token(user.entity_id),
        refresh_token = create_refresh_token(user.entity_id),
        user          = UserPublic.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """Обновление access токена через refresh токен."""
    error = HTTPException(status_code=401, detail="Невалидный refresh токен")

    # Проверяем blacklist
    if is_token_blacklisted(data.refresh_token):
        raise error

    try:
        payload   = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise error
        entity_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise error

    user = get_user_by_entity_id(db, entity_id)
    if not user or user.status != "active":
        raise error

    return TokenResponse(
        access_token  = create_access_token(entity_id),
        refresh_token = create_refresh_token(entity_id),
        user          = UserPublic.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(data: LogoutRequest):
    """
    Инвалидация refresh токена через Redis blacklist.
    После logout — токен больше не работает для /refresh.
    """
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Передай refresh токен")

        # Считаем сколько секунд токен ещё живёт
        import time
        expire_seconds = max(0, int(payload["exp"] - time.time()))

        if expire_seconds > 0:
            blacklist_token(data.refresh_token, expire_seconds)

    except jwt.InvalidTokenError:
        # Токен уже истёк — просто игнорируем
        pass

    return MessageResponse(message="Выход выполнен успешно")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data:         ChangePasswordRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Смена пароля авторизованного пользователя.
    Требует старый пароль для подтверждения.
    Создаёт новую версию пользователя.
    """
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code = 400,
            detail      = "Неверный текущий пароль",
        )

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code = 400,
            detail      = "Новый пароль должен отличаться от старого",
        )

    create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = current_user.entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "password_change",
        hashed_password = hash_password(data.new_password),
    )

    return MessageResponse(message="Пароль успешно изменён")


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/hour")  # Максимум 3 запроса на сброс пароля в час
def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db:   Session = Depends(get_db),
):
    """
    Запрос сброса пароля.
    Отправляет письмо со ссылкой если email найден.

    Всегда возвращает 200 — не раскрываем существует ли email.
    """
    user = get_user_by_email(db, data.email)

    if user and user.status == "active":
        # Генерируем криптографически случайный токен
        reset_token    = secrets.token_urlsafe(32)
        expire_seconds = settings.RESET_PASSWORD_EXPIRE_MINUTES * 60

        # Сохраняем в Redis
        save_reset_token(
            token          = reset_token,
            entity_id      = user.entity_id,
            expire_seconds = expire_seconds,
        )

        # Отправляем письмо
        try:
            send_reset_password_email(
                to          = user.email,
                reset_token = reset_token,
                username    = user.username,
            )
        except Exception:
            # Если SMTP не настроен — не падаем
            # В продакшне нужно логировать ошибку
            pass

    # Всегда одинаковый ответ — безопасность
    return MessageResponse(
        message="Если email зарегистрирован — письмо отправлено"
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    data: ResetPasswordRequest,
    db:   Session = Depends(get_db),
):
    """
    Сброс пароля по токену из письма.
    Токен одноразовый — удаляется после использования.
    """
    entity_id = get_reset_token_entity_id(data.token)
    if not entity_id:
        raise HTTPException(
            status_code = 400,
            detail      = "Токен недействителен или истёк",
        )

    user = get_user_by_entity_id(db, entity_id)
    if not user or user.status != "active":
        raise HTTPException(
            status_code = 400,
            detail      = "Пользователь не найден",
        )

    # Создаём новую версию с новым паролем
    create_new_version(
        db              = db,
        model_class     = User,
        entity_id       = entity_id,
        changed_by_id   = entity_id,
        change_reason   = "password_reset",
        hashed_password = hash_password(data.new_password),
    )

    # Удаляем токен — одноразовый
    delete_reset_token(data.token)

    return MessageResponse(message="Пароль успешно сброшен")