# app/api/v1/user_settings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.user_settings import UserNotificationSettings
from app.schemas.user_settings import (
    UserNotificationSettingsPublic,
    UserNotificationSettingsUpdate,
)
from app.api.deps import get_current_user
from app.services.versioning import create_new_version

router = APIRouter(prefix="/settings", tags=["user-settings"])


@router.get("/notifications", response_model=UserNotificationSettingsPublic)
def get_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить настройки уведомлений текущего пользователя"""
    settings = (
        db.query(UserNotificationSettings)
        .filter_by(user_entity_id=current_user.entity_id, is_current=True)
        .first()
    )

    if not settings:
        # Создать настройки по умолчанию
        entity_id = UserNotificationSettings.next_entity_id(db)
        settings = UserNotificationSettings(
            entity_id=entity_id,
            version=1,
            is_current=True,
            user_entity_id=current_user.entity_id,
            changed_by_id=current_user.entity_id,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.patch("/notifications", response_model=UserNotificationSettingsPublic)
def update_notification_settings(
    data: UserNotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить настройки уведомлений"""
    settings = (
        db.query(UserNotificationSettings)
        .filter_by(user_entity_id=current_user.entity_id, is_current=True)
        .first()
    )

    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")

    # Подготовить данные для обновления
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return settings

    # Создать новую версию с обновлёнными данными
    updated = create_new_version(
        db=db,
        model_class=UserNotificationSettings,
        entity_id=settings.entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="settings_updated",
        **update_data,
    )

    return updated
