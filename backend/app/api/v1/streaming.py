# app/api/v1/streaming.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.database import get_db
from app.models.media import ProblemMedia, MediaType
from app.models.problem import Problem
from app.services.storage import get_storage

router = APIRouter(prefix="/problems", tags=["streaming"])


async def ranged_file_reader(file_path: str, start: int, end: int, chunk_size: int = 8192):
    """
    Генератор для чтения файла по частям с поддержкой Range requests.
    Используется для стриминга видео с возможностью перемотки.
    """
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1

        while remaining > 0:
            chunk = f.read(min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


@router.get("/{problem_entity_id}/media/{media_entity_id}/stream")
async def stream_video(
    request:           Request,
    problem_entity_id: int,
    media_entity_id:   int,
    db:                Session = Depends(get_db),
):
    """
    Стриминг видео с поддержкой HTTP Range requests.

    Позволяет:
    - Перематывать видео без полной загрузки
    - Начинать воспроизведение с любого момента
    - Экономить трафик

    Работает только для локального хранилища (local storage).
    Для Cloudinary используется прямой URL с их CDN.
    """
    # Проверить что проблема существует
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Получить медиа
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

    # Только для видео
    if media.media_type != MediaType.video:
        raise HTTPException(
            status_code=400,
            detail="Стриминг доступен только для видео"
        )

    # Получить storage backend
    storage = get_storage()

    # Для Cloudinary - редирект на их CDN (они поддерживают Range requests)
    if storage.__class__.__name__ == "CloudinaryStorage":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=media.url)

    # Для локального хранилища - реализуем Range requests
    if storage.__class__.__name__ != "LocalStorage":
        raise HTTPException(
            status_code=501,
            detail="Стриминг поддерживается только для local и cloudinary storage"
        )

    # Получить путь к файлу
    # URL формата: /media/problems/{problem_id}/{entity_id}_video.mp4
    file_path = Path(storage.base_path) / media.url.replace("/media/", "")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    file_size = file_path.stat().st_size

    # Парсинг Range header
    range_header = request.headers.get("range")

    if not range_header:
        # Без Range - отдаем весь файл
        def file_iterator():
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(file_size),
            }
        )

    # Парсинг Range: bytes=start-end
    try:
        range_str = range_header.replace("bytes=", "")
        start_str, end_str = range_str.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1

        # Валидация
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(
                status_code=416,
                detail="Requested Range Not Satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"}
            )

        content_length = end - start + 1

        return StreamingResponse(
            ranged_file_reader(str(file_path), start, end),
            status_code=206,  # Partial Content
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
            }
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Range header format"
        )


@router.get("/{problem_entity_id}/media/{media_entity_id}/hls")
async def get_hls_playlist(
    problem_entity_id: int,
    media_entity_id:   int,
    db:                Session = Depends(get_db),
):
    """
    Получить HLS playlist для адаптивного стриминга.

    Требует предварительной обработки видео через Celery задачу.
    Если видео не обработано (is_processed != 1) - возвращает ошибку.

    HLS (HTTP Live Streaming) позволяет:
    - Адаптивный битрейт (качество подстраивается под скорость интернета)
    - Быстрый старт воспроизведения
    - Поддержка всех современных браузеров
    """
    # Проверить что проблема существует
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Получить медиа
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

    # Только для видео
    if media.media_type != MediaType.video:
        raise HTTPException(
            status_code=400,
            detail="HLS доступен только для видео"
        )

    # Проверить что видео обработано
    if media.is_processed != 1:
        if media.is_processed == 0:
            raise HTTPException(
                status_code=202,
                detail="Видео обрабатывается, попробуйте позже"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Ошибка обработки видео"
            )

    # Проверить что HLS URL существует
    if not media.hls_url:
        raise HTTPException(
            status_code=404,
            detail="HLS playlist не найден"
        )

    # Для Cloudinary - редирект на их HLS
    storage = get_storage()
    if storage.__class__.__name__ == "CloudinaryStorage":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=media.hls_url)

    # Для локального хранилища - отдать .m3u8 файл
    file_path = Path(storage.base_path) / media.hls_url.replace("/media/", "")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="HLS playlist не найден на диске")

    with open(file_path, "r") as f:
        playlist_content = f.read()

    return StreamingResponse(
        iter([playlist_content]),
        media_type="application/vnd.apple.mpegurl",
        headers={
            "Cache-Control": "no-cache",
        }
    )
