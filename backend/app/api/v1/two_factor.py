# app/api/v1/two_factor.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.totp import (
    generate_totp_secret,
    generate_totp_uri,
    verify_totp_code,
    generate_backup_codes,
    hash_backup_code,
    verify_backup_code,
)
from app.services.versioning import create_new_version

router = APIRouter(prefix="/2fa", tags=["2fa"])


class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_uri: str
    backup_codes: list[str]


class TwoFactorVerifyRequest(BaseModel):
    code: str


class TwoFactorDisableRequest(BaseModel):
    password: str
    code: str | None = None


class MessageResponse(BaseModel):
    message: str


@router.post("/setup", response_model=TwoFactorSetupResponse)
def setup_2fa(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Начать настройку 2FA.
    Генерирует секрет и QR код URI для сканирования в приложении.
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA уже включена",
        )

    # Генерируем секрет и резервные коды
    secret = generate_totp_secret()
    qr_uri = generate_totp_uri(secret, current_user.email)
    backup_codes = generate_backup_codes(10)

    # Хешируем резервные коды для хранения
    hashed_codes = [hash_backup_code(code) for code in backup_codes]

    # Сохраняем секрет (но пока не активируем)
    create_new_version(
        db=db,
        model_class=User,
        entity_id=current_user.entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="2fa_setup_initiated",
        totp_secret=secret,
        backup_codes=hashed_codes,
    )

    return TwoFactorSetupResponse(
        secret=secret,
        qr_uri=qr_uri,
        backup_codes=backup_codes,
    )


@router.post("/enable", response_model=MessageResponse)
def enable_2fa(
    data: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Активировать 2FA после проверки кода.
    Пользователь должен ввести код из приложения для подтверждения.
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA уже включена",
        )

    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала вызовите /2fa/setup",
        )

    # Проверяем код
    if not verify_totp_code(current_user.totp_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код",
        )

    # Активируем 2FA
    create_new_version(
        db=db,
        model_class=User,
        entity_id=current_user.entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="2fa_enabled",
        totp_enabled=True,
    )

    return MessageResponse(message="2FA успешно включена")


@router.post("/disable", response_model=MessageResponse)
def disable_2fa(
    data: TwoFactorDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отключить 2FA.
    Требует пароль и код (или резервный код).
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA не включена",
        )

    # Проверяем пароль
    from app.services.auth import verify_password
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
        )

    # Проверяем код если передан
    if data.code:
        if not verify_totp_code(current_user.totp_secret, data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный код",
            )

    # Отключаем 2FA
    create_new_version(
        db=db,
        model_class=User,
        entity_id=current_user.entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="2fa_disabled",
        totp_enabled=False,
        totp_secret=None,
        backup_codes=None,
    )

    return MessageResponse(message="2FA отключена")


@router.post("/verify", response_model=MessageResponse)
def verify_2fa_code(
    data: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Проверить 2FA код (для тестирования).
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA не включена",
        )

    # Проверяем обычный код
    if verify_totp_code(current_user.totp_secret, data.code):
        return MessageResponse(message="Код верный")

    # Проверяем резервные коды
    if current_user.backup_codes:
        for i, hashed_code in enumerate(current_user.backup_codes):
            if verify_backup_code(data.code, hashed_code):
                # Удаляем использованный резервный код
                remaining_codes = [
                    c for j, c in enumerate(current_user.backup_codes) if j != i
                ]
                create_new_version(
                    db=db,
                    model_class=User,
                    entity_id=current_user.entity_id,
                    changed_by_id=current_user.entity_id,
                    change_reason="backup_code_used",
                    backup_codes=remaining_codes,
                )
                return MessageResponse(message="Резервный код принят")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неверный код",
    )


@router.get("/status")
def get_2fa_status(current_user: User = Depends(get_current_user)):
    """Получить статус 2FA для текущего пользователя"""
    return {
        "enabled": current_user.totp_enabled,
        "backup_codes_count": len(current_user.backup_codes) if current_user.backup_codes else 0,
    }
