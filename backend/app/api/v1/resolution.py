# app/api/v1/resolution.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

from app.database import get_db
from app.models.media import ProblemMedia, MediaStatus, MediaCategory
from app.models.problem import Problem, ProblemStatus, ResolverType
from app.models.user import User, UserRole
from app.schemas.media import MediaPublic
from app.services.versioning import create_new_version
from app.services.media import validate_file, extract_exif
from app.services.storage import get_storage
from app.api.deps import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/problems", tags=["resolution"])


@router.post("/{problem_entity_id}/start-resolution", status_code=200)
@limiter.limit("10/hour")
def start_problem_resolution(
    request:           Request,
    problem_entity_id: int,
    resolver_type:     ResolverType = Form(...),
    resolution_note:   Optional[str] = Form(None),
    db:                Session = Depends(get_db),
    current_user:      User = Depends(get_current_user),
):
    """
    Начать решение проблемы.

    Доступно для:
    - volunteer: может начать решение как волонтер
    - official: может начать решение как официальная организация
    - moderator/admin: могут начать решение от любого имени

    Изменяет статус проблемы на 'in_progress'.
    """
    # Проверка прав
    allowed_roles = (UserRole.volunteer, UserRole.moderator, UserRole.official, UserRole.admin)
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только volunteer, official, moderator или admin могут начать решение проблемы"
        )

    # Получить проблему
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверить что проблема еще не решена
    if problem.status in (ProblemStatus.solved, ProblemStatus.rejected):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Проблема уже в статусе '{problem.status.value}'"
        )

    # Проверить что resolver_type соответствует роли
    if current_user.role == UserRole.volunteer and resolver_type != ResolverType.volunteer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Волонтер может начать решение только как 'volunteer'"
        )

    if current_user.role == UserRole.official and resolver_type != ResolverType.official_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Официальная организация может начать решение только как 'official_org'"
        )

    # Обновить проблему
    updated_problem = create_new_version(
        db=db,
        model_class=Problem,
        entity_id=problem_entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="resolution_started",
        status=ProblemStatus.in_progress,
        resolved_by_entity_id=current_user.entity_id,
        resolver_type=resolver_type,
        resolution_note=resolution_note,
    )

    # Отправить WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="status_updated",
            data={
                "status": ProblemStatus.in_progress.value,
                "resolver_id": current_user.entity_id,
                "resolver_type": resolver_type.value,
            }
        )
    except Exception:
        pass

    return {
        "message": "Решение проблемы начато",
        "problem_id": problem_entity_id,
        "status": updated_problem.status.value,
        "resolver_type": resolver_type.value,
    }


@router.post("/{problem_entity_id}/complete-resolution", status_code=200)
@limiter.limit("10/hour")
def complete_problem_resolution(
    request:           Request,
    problem_entity_id: int,
    resolution_note:   Optional[str] = Form(None),
    db:                Session = Depends(get_db),
    current_user:      User = Depends(get_current_user),
):
    """
    Завершить решение проблемы.

    Доступно для:
    - Пользователь который начал решение (resolved_by_entity_id)
    - moderator/admin

    Изменяет статус проблемы на 'solved'.
    Устанавливает resolved_at в текущее время.
    """
    # Проверка прав
    allowed_roles = (UserRole.volunteer, UserRole.moderator, UserRole.official, UserRole.admin)
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только volunteer, official, moderator или admin могут завершить решение"
        )

    # Получить проблему
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверить что проблема в процессе решения
    if problem.status != ProblemStatus.in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Проблема должна быть в статусе 'in_progress', текущий статус: '{problem.status.value}'"
        )

    # Проверить права на завершение
    is_resolver = problem.resolved_by_entity_id == current_user.entity_id
    is_privileged = current_user.role in (UserRole.admin, UserRole.moderator)

    if not (is_resolver or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только пользователь начавший решение или модератор/админ могут завершить решение"
        )

    # Обновить проблему
    updated_problem = create_new_version(
        db=db,
        model_class=Problem,
        entity_id=problem_entity_id,
        changed_by_id=current_user.entity_id,
        change_reason="resolution_completed",
        status=ProblemStatus.solved,
        resolved_at=datetime.now(timezone.utc),
        resolution_note=resolution_note or problem.resolution_note,
    )

    # Отправить WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="status_updated",
            data={
                "status": ProblemStatus.solved.value,
                "resolved_at": updated_problem.resolved_at.isoformat(),
            }
        )
    except Exception:
        pass

    return {
        "message": "Проблема решена",
        "problem_id": problem_entity_id,
        "status": updated_problem.status.value,
        "resolved_at": updated_problem.resolved_at.isoformat(),
    }


@router.post("/{problem_entity_id}/upload-progress", response_model=MediaPublic, status_code=201)
@limiter.limit("20/hour")
async def upload_progress_media(
    request:           Request,
    problem_entity_id: int,
    file:              UploadFile = File(...),
    caption:           Optional[str] = Form(None),
    db:                Session = Depends(get_db),
    current_user:      User = Depends(get_current_user),
):
    """
    Загрузить фото/видео процесса работы над проблемой.

    Доступно только для:
    - volunteer, official, moderator, admin

    Проблема должна быть в статусе 'in_progress' или 'solved'.
    Автоматически устанавливает media_category='in_progress'.
    """
    # Проверка прав
    allowed_roles = (UserRole.volunteer, UserRole.moderator, UserRole.official, UserRole.admin)
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только volunteer, official, moderator или admin могут загружать медиа процесса"
        )

    # Получить проблему
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверить статус проблемы
    if problem.status not in (ProblemStatus.in_progress, ProblemStatus.solved):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Медиа процесса можно загружать только для проблем в статусе 'in_progress' или 'solved'"
        )

    # Загрузить файл
    file_bytes = await file.read()
    media_type = validate_file(file, file_bytes)

    entity_id = ProblemMedia.next_entity_id(db)

    # Получить display_order
    max_order = db.query(ProblemMedia.display_order).filter_by(
        problem_entity_id=problem_entity_id,
        is_current=True,
        media_category=MediaCategory.in_progress
    ).order_by(ProblemMedia.display_order.desc()).first()
    display_order = (max_order[0] + 1) if max_order else 0

    # Загрузка через storage
    storage = get_storage()
    cloud_result = storage.upload(
        file_bytes=file_bytes,
        entity_id=entity_id,
        problem_entity_id=problem_entity_id,
        media_type=media_type,
        content_type=file.content_type or "",
    )

    # EXIF для фото
    exif_data = {}
    if media_type == "photo":
        exif_data = extract_exif(file_bytes)

    media = ProblemMedia(
        entity_id=entity_id,
        version=1,
        is_current=True,
        problem_entity_id=problem_entity_id,
        uploader_entity_id=current_user.entity_id,
        media_type=media_type,
        media_category=MediaCategory.in_progress,
        status=MediaStatus.active,
        url=cloud_result["url"],
        thumbnail_url=cloud_result["thumbnail_url"],
        file_size=cloud_result["file_size"],
        caption=caption,
        display_order=display_order,
        exif_lat=exif_data.get("exif_lat"),
        exif_lon=exif_data.get("exif_lon"),
        exif_taken_at=exif_data.get("exif_taken_at"),
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    # WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="media_added",
            data={
                "media_id": media.entity_id,
                "media_category": "in_progress",
                "uploader_id": current_user.entity_id,
            }
        )
    except Exception:
        pass

    return media


@router.post("/{problem_entity_id}/upload-result", response_model=MediaPublic, status_code=201)
@limiter.limit("20/hour")
async def upload_result_media(
    request:           Request,
    problem_entity_id: int,
    file:              UploadFile = File(...),
    caption:           Optional[str] = Form(None),
    db:                Session = Depends(get_db),
    current_user:      User = Depends(get_current_user),
):
    """
    Загрузить фото/видео результата работы (после решения проблемы).

    Доступно только для:
    - volunteer, official, moderator, admin

    Проблема должна быть в статусе 'solved'.
    Автоматически устанавливает media_category='result'.
    """
    # Проверка прав
    allowed_roles = (UserRole.volunteer, UserRole.moderator, UserRole.official, UserRole.admin)
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только volunteer, official, moderator или admin могут загружать медиа результата"
        )

    # Получить проблему
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверить статус проблемы
    if problem.status != ProblemStatus.solved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Медиа результата можно загружать только для решенных проблем"
        )

    # Загрузить файл
    file_bytes = await file.read()
    media_type = validate_file(file, file_bytes)

    entity_id = ProblemMedia.next_entity_id(db)

    # Получить display_order
    max_order = db.query(ProblemMedia.display_order).filter_by(
        problem_entity_id=problem_entity_id,
        is_current=True,
        media_category=MediaCategory.result
    ).order_by(ProblemMedia.display_order.desc()).first()
    display_order = (max_order[0] + 1) if max_order else 0

    # Загрузка через storage
    storage = get_storage()
    cloud_result = storage.upload(
        file_bytes=file_bytes,
        entity_id=entity_id,
        problem_entity_id=problem_entity_id,
        media_type=media_type,
        content_type=file.content_type or "",
    )

    # EXIF для фото
    exif_data = {}
    if media_type == "photo":
        exif_data = extract_exif(file_bytes)

    media = ProblemMedia(
        entity_id=entity_id,
        version=1,
        is_current=True,
        problem_entity_id=problem_entity_id,
        uploader_entity_id=current_user.entity_id,
        media_type=media_type,
        media_category=MediaCategory.result,
        status=MediaStatus.active,
        url=cloud_result["url"],
        thumbnail_url=cloud_result["thumbnail_url"],
        file_size=cloud_result["file_size"],
        caption=caption,
        display_order=display_order,
        exif_lat=exif_data.get("exif_lat"),
        exif_lon=exif_data.get("exif_lon"),
        exif_taken_at=exif_data.get("exif_taken_at"),
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    # WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="media_added",
            data={
                "media_id": media.entity_id,
                "media_category": "result",
                "uploader_id": current_user.entity_id,
            }
        )
    except Exception:
        pass

    return media


@router.get("/{problem_entity_id}/media/by-category", response_model=List[MediaPublic])
def get_media_by_category(
    problem_entity_id: int,
    category:          MediaCategory,
    db:                Session = Depends(get_db),
):
    """
    Получить медиа проблемы по категории.

    Категории:
    - problem: Исходная проблема
    - in_progress: Процесс работы
    - result: Результат работы
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    media_list = (
        db.query(ProblemMedia)
        .filter_by(
            problem_entity_id=problem_entity_id,
            media_category=category,
            is_current=True,
            status=MediaStatus.active,
        )
        .order_by(ProblemMedia.display_order.asc(), ProblemMedia.created_at.asc())
        .all()
    )

    return media_list
