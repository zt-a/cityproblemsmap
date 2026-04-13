# app/services/auth.py
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User


# Контекст для хэширования паролей — argon2 надёжнее bcrypt
pwd_hash = PasswordHash((Argon2Hasher(),))


# ── Пароли ──────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_hash.verify(plain, hashed)


# ── JWT токены ───────────────────────────────────────────

def create_access_token(entity_id: int) -> str:
    """
    Короткоживущий токен — 30 минут.
    Используется для каждого запроса к API.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(entity_id),  # subject — entity_id пользователя
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(entity_id: int) -> str:
    """
    Долгоживущий токен — 30 дней.
    Используется только для получения нового access токена.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(entity_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Декодирует токен. Кидает jwt.InvalidTokenError если невалидный или просроченный.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ── Работа с пользователем ───────────────────────────────

def get_user_by_email(db: Session, email: str) -> User | None:
    """Возвращает текущую версию пользователя по email."""
    return (
        db.query(User)
        .filter_by(email=email, is_current=True)
        .first()
    )


def get_user_by_entity_id(db: Session, entity_id: int) -> User | None:
    """Возвращает текущую версию пользователя по entity_id."""
    return (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Проверяет email + пароль.
    Возвращает пользователя если всё ок, None если нет.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.status != "active":
        return None
    return user