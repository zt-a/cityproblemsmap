# app/api/v1/media.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.media import ProblemMedia, MediaStatus, MediaCategory
from app.models.problem import Problem, ProblemStatus
from app.models.user import User, UserRole
from app.schemas.media import MediaPublic, MediaUpdate, MediaReorder
from app.services.versioning import create_new_version
from app.services.media import validate_file, extract_exif, verify_geo_match
from app.services.storage import get_storage
from app.api.deps import get_current_user
from app.middleware.rate_limit import limiter
from geoalchemy2.shape import to_shape
from app.workers.tasks_video import process_video

router = APIRouter(prefix="/problems", tags=["media"])


def _get_problem_coords(problem: Problem) -> tuple[float, float]:
    if problem.location is None:
        return 0.0, 0.0
    point = to_shape(problem.location)
    return point.y, point.x


@router.post("/{problem_entity_id}/media", response_model=MediaPublic, status_code=201)
@limiter.limit("20/hour")  # Защита от спама медиафайлами
async def upload_media(
    request:           Request,
    problem_entity_id: int,
    file:              UploadFile = File(...),
    caption:           Optional[str] = Form(None),
    category:          MediaCategory = Form(MediaCategory.problem),
    db:                Session    = Depends(get_db),
    current_user:      User       = Depends(get_current_user),
):
    """
    Загрузить фото или видео к проблеме.

    Категории медиа:
    - problem: Исходная проблема (любой пользователь)
    - in_progress: Процесс работы (только volunteer, moderator, official, admin)
    - result: Результат работы (только volunteer, moderator, official, admin)

    Хранилище выбирается через MEDIA_STORAGE в .env:
    - local      — локальная папка (разработка)
    - cloudinary — облако (продакшн)
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Проверка прав для загрузки медиа процесса/результата
    if category in (MediaCategory.in_progress, MediaCategory.result):
        allowed_roles = (UserRole.volunteer, UserRole.moderator, UserRole.official, UserRole.admin)
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Только {', '.join(allowed_roles)} могут загружать медиа категории '{category.value}'"
            )

        # Проверка статуса проблемы
        if category == MediaCategory.in_progress and problem.status not in (ProblemStatus.in_progress, ProblemStatus.solved):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Медиа 'in_progress' можно загружать только для проблем в статусе 'in_progress' или 'solved'"
            )

        if category == MediaCategory.result and problem.status != ProblemStatus.solved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Медиа 'result' можно загружать только для решенных проблем"
            )

    file_bytes = await file.read()
    media_type = validate_file(file, file_bytes)

    # EXIF + геопроверка только для фото
    exif_data = {}
    if media_type == "photo":
        exif_data = extract_exif(file_bytes)

        if exif_data["exif_lat"] is not None:
            problem_lat, problem_lon = _get_problem_coords(problem)
            if not verify_geo_match(
                exif_lat       = exif_data["exif_lat"],
                exif_lon       = exif_data["exif_lon"],
                problem_lat    = problem_lat,
                problem_lon    = problem_lon,
                max_distance_m = 1000,
            ):
                raise HTTPException(
                    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail      = "Фото сделано слишком далеко от места проблемы (>1км)",
                )

    entity_id = ProblemMedia.next_entity_id(db)

    # Получить текущий максимальный display_order для этой проблемы
    max_order = db.query(ProblemMedia.display_order).filter_by(
        problem_entity_id=problem_entity_id,
        is_current=True
    ).order_by(ProblemMedia.display_order.desc()).first()
    display_order = (max_order[0] + 1) if max_order else 0

    # Загрузка через выбранный бэкенд
    storage      = get_storage()
    cloud_result = storage.upload(
        file_bytes        = file_bytes,
        entity_id         = entity_id,
        problem_entity_id = problem_entity_id,
        media_type        = media_type,
        content_type      = file.content_type or "",
    )

    media = ProblemMedia(
        entity_id          = entity_id,
        version            = 1,
        is_current         = True,
        problem_entity_id  = problem_entity_id,
        uploader_entity_id = current_user.entity_id,
        media_type         = media_type,
        media_category     = category,
        status             = MediaStatus.active,
        url                = cloud_result["url"],
        thumbnail_url      = cloud_result["thumbnail_url"],
        file_size          = cloud_result["file_size"],
        caption            = caption,
        display_order      = display_order,
        exif_lat           = exif_data.get("exif_lat"),
        exif_lon           = exif_data.get("exif_lon"),
        exif_taken_at      = exif_data.get("exif_taken_at"),
    )
    db.add(media)
    db.commit()
    db.refresh(media)

    # Запустить обработку видео в фоне (если это видео и local storage)
    if media_type == "video" and cloud_result.get("local_path"):
        process_video.delay(
            video_path=cloud_result["local_path"],
            problem_entity_id=problem_entity_id,
            media_id=media.id
        )

    return media


@router.get("/{problem_entity_id}/media", response_model=list[MediaPublic])
def get_problem_media(
    problem_entity_id: int,
    db:                Session = Depends(get_db),
):
    """Все активные медиафайлы проблемы."""
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    return (
        db.query(ProblemMedia)
        .filter_by(
            problem_entity_id = problem_entity_id,
            is_current        = True,
            status            = MediaStatus.active,
        )
        .order_by(ProblemMedia.display_order.asc(), ProblemMedia.created_at.asc())
        .all()
    )


@router.delete(
    "/{problem_entity_id}/media/{media_entity_id}",
    response_model=MediaPublic,
)
def remove_media(
    problem_entity_id: int,
    media_entity_id:   int,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """Мягкое удаление медиафайла — status=removed."""
    media = (
        db.query(ProblemMedia)
        .filter_by(
            entity_id         = media_entity_id,
            problem_entity_id = problem_entity_id,
            is_current        = True,
        )
        .first()
    )
    if not media:
        raise HTTPException(status_code=404, detail="Медиафайл не найден")

    is_uploader      = media.uploader_entity_id == current_user.entity_id
    is_privileged    = current_user.role in (UserRole.admin, UserRole.moderator)
    problem          = db.query(Problem).filter_by(
        entity_id=problem_entity_id, is_current=True
    ).first()
    is_problem_author = problem and problem.author_entity_id == current_user.entity_id

    if not any([is_uploader, is_privileged, is_problem_author]):
        raise HTTPException(status_code=403, detail="Нет прав на удаление")

    return create_new_version(
        db            = db,
        model_class   = ProblemMedia,
        entity_id     = media_entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "user_removed",
        status        = MediaStatus.removed,
    )


@router.patch(
    "/{problem_entity_id}/media/{media_entity_id}",
    response_model=MediaPublic,
)
@limiter.limit("20/hour")  # Защита от спама заменами
async def replace_media(
    request:           Request,
    problem_entity_id: int,
    media_entity_id:   int,
    file:              Optional[UploadFile] = File(None),
    caption:           Optional[str] = Form(None),
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Заменить медиафайл или обновить caption.

    - Если передан file: загружает новый файл, старый помечается status=replaced
    - Если передан только caption: обновляет подпись без замены файла
    - Только uploader или автор проблемы может заменять медиа
    """
    media = (
        db.query(ProblemMedia)
        .filter_by(
            entity_id         = media_entity_id,
            problem_entity_id = problem_entity_id,
            is_current        = True,
        )
        .first()
    )
    if not media:
        raise HTTPException(status_code=404, detail="Медиафайл не найден")

    # Проверка прав
    is_uploader = media.uploader_entity_id == current_user.entity_id
    problem = db.query(Problem).filter_by(
        entity_id=problem_entity_id, is_current=True
    ).first()
    is_problem_author = problem and problem.author_entity_id == current_user.entity_id

    if not any([is_uploader, is_problem_author]):
        raise HTTPException(status_code=403, detail="Нет прав на изменение")

    update_fields = {}

    # Если передан новый файл - загружаем
    if file:
        file_bytes = await file.read()
        media_type = validate_file(file, file_bytes)

        # Проверка что тип медиа не изменился
        if media_type != media.media_type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Нельзя заменить {media.media_type.value} на {media_type}"
            )

        # EXIF + геопроверка для фото
        exif_data = {}
        if media_type == "photo":
            exif_data = extract_exif(file_bytes)

            if exif_data["exif_lat"] is not None:
                problem_lat, problem_lon = _get_problem_coords(problem)
                if not verify_geo_match(
                    exif_lat       = exif_data["exif_lat"],
                    exif_lon       = exif_data["exif_lon"],
                    problem_lat    = problem_lat,
                    problem_lon    = problem_lon,
                    max_distance_m = 1000,
                ):
                    raise HTTPException(
                        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail      = "Фото сделано слишком далеко от места проблемы (>1км)",
                    )

        # Загрузка нового файла
        storage = get_storage()
        cloud_result = storage.upload(
            file_bytes        = file_bytes,
            entity_id         = media_entity_id,
            problem_entity_id = problem_entity_id,
            media_type        = media_type,
            content_type      = file.content_type or "",
        )

        update_fields.update({
            "url":           cloud_result["url"],
            "thumbnail_url": cloud_result["thumbnail_url"],
            "file_size":     cloud_result["file_size"],
            "status":        MediaStatus.active,
        })

        if media_type == "photo" and exif_data:
            update_fields.update({
                "exif_lat":      exif_data.get("exif_lat"),
                "exif_lon":      exif_data.get("exif_lon"),
                "exif_taken_at": exif_data.get("exif_taken_at"),
            })

        # Старый файл помечаем replaced
        change_reason = "media_replaced"
    else:
        change_reason = "caption_updated"

    # Обновить caption если передан
    if caption is not None:
        update_fields["caption"] = caption

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно передать file или caption"
        )

    # Создать новую версию
    updated = create_new_version(
        db            = db,
        model_class   = ProblemMedia,
        entity_id     = media_entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = change_reason,
        **update_fields,
    )

    return updated


@router.patch(
    "/{problem_entity_id}/media/reorder",
    response_model=list[MediaPublic],
)
def reorder_media(
    problem_entity_id: int,
    data:              MediaReorder,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Изменить порядок отображения медиафайлов.
    Передать список entity_id в нужном порядке.
    Только автор проблемы может менять порядок.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    if problem.author_entity_id != current_user.entity_id:
        raise HTTPException(
            status_code=403,
            detail="Только автор проблемы может менять порядок медиа"
        )

    # Проверить что все media_id принадлежат этой проблеме
    media_list = (
        db.query(ProblemMedia)
        .filter(
            ProblemMedia.entity_id.in_(data.media_order),
            ProblemMedia.problem_entity_id == problem_entity_id,
            ProblemMedia.is_current == True,
        )
        .all()
    )

    if len(media_list) != len(data.media_order):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некоторые media_id не найдены или не принадлежат этой проблеме"
        )

    # Обновить display_order для каждого медиа
    updated_media = []
    for order, entity_id in enumerate(data.media_order):
        updated = create_new_version(
            db            = db,
            model_class   = ProblemMedia,
            entity_id     = entity_id,
            changed_by_id = current_user.entity_id,
            change_reason = "order_changed",
            display_order = order,
        )
        updated_media.append(updated)

    return updated_media