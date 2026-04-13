# app/workers/tasks_video.py
from celery import shared_task
import subprocess
import os
from pathlib import Path
from PIL import Image
import logging

from app.config import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_video(self, video_path: str, problem_entity_id: int, media_id: int):
    """
    Обработка видео:
    1. Генерация thumbnail
    2. Транскодинг в H.264 (если нужно)
    3. Генерация HLS playlist (опционально)
    """
    try:
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # 1. Генерация thumbnail
        thumbnail_path = generate_thumbnail(video_path)
        logger.info(f"Generated thumbnail: {thumbnail_path}")

        # 2. Транскодинг (если видео не в H.264)
        transcoded_path = transcode_video(video_path)
        if transcoded_path:
            logger.info(f"Transcoded video: {transcoded_path}")

        # 3. Генерация HLS (для стриминга)
        hls_path = generate_hls(transcoded_path or video_path)
        if hls_path:
            logger.info(f"Generated HLS playlist: {hls_path}")

        return {
            "status": "success",
            "thumbnail": str(thumbnail_path),
            "transcoded": str(transcoded_path) if transcoded_path else None,
            "hls": str(hls_path) if hls_path else None
        }

    except Exception as exc:
        logger.error(f"Video processing failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


def generate_thumbnail(video_path: str, time_offset: str = "00:00:01") -> Path:
    """
    Генерация thumbnail из видео с помощью ffmpeg.

    Args:
        video_path: Путь к видео файлу
        time_offset: Временная метка для скриншота (по умолчанию 1 секунда)

    Returns:
        Path к созданному thumbnail
    """
    video_file = Path(video_path)
    thumbnail_path = video_file.parent / f"{video_file.stem}_thumb.jpg"

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-ss", time_offset,
        "-vframes", "1",
        "-vf", "scale=640:-1",  # Ширина 640px, высота пропорциональна
        "-q:v", "2",  # Качество JPEG (2-5 хорошее)
        "-y",  # Перезаписать если существует
        str(thumbnail_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg thumbnail generation failed: {result.stderr}")

    # Оптимизация thumbnail с помощью Pillow
    with Image.open(thumbnail_path) as img:
        img.thumbnail((640, 640), Image.Resampling.LANCZOS)
        img.save(thumbnail_path, "JPEG", quality=85, optimize=True)

    return thumbnail_path


def transcode_video(video_path: str, target_codec: str = "h264") -> Path | None:
    """
    Транскодинг видео в H.264 для совместимости.

    Args:
        video_path: Путь к исходному видео
        target_codec: Целевой кодек (по умолчанию h264)

    Returns:
        Path к транскодированному видео или None если транскодинг не нужен
    """
    # Проверка текущего кодека
    cmd_probe = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]

    result = subprocess.run(cmd_probe, capture_output=True, text=True)
    current_codec = result.stdout.strip()

    # Если уже H.264 - пропускаем
    if current_codec == "h264":
        logger.info(f"Video already in H.264, skipping transcode: {video_path}")
        return None

    video_file = Path(video_path)
    output_path = video_file.parent / f"{video_file.stem}_transcoded.mp4"

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-c:v", "libx264",  # H.264 кодек
        "-preset", "medium",  # Баланс скорость/качество
        "-crf", "23",  # Качество (18-28, меньше = лучше)
        "-c:a", "aac",  # AAC аудио
        "-b:a", "128k",  # Битрейт аудио
        "-movflags", "+faststart",  # Оптимизация для веб
        "-y",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg transcode failed: {result.stderr}")

    return output_path


def generate_hls(video_path: str, segment_duration: int = 6) -> Path | None:
    """
    Генерация HLS playlist для адаптивного стриминга.

    Args:
        video_path: Путь к видео файлу
        segment_duration: Длительность сегмента в секундах

    Returns:
        Path к .m3u8 playlist файлу
    """
    video_file = Path(video_path)
    hls_dir = video_file.parent / f"{video_file.stem}_hls"
    hls_dir.mkdir(exist_ok=True)

    playlist_path = hls_dir / "playlist.m3u8"

    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-hls_time", str(segment_duration),
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(hls_dir / "segment_%03d.ts"),
        "-y",
        str(playlist_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.warning(f"HLS generation failed: {result.stderr}")
        return None

    return playlist_path


@shared_task
def cleanup_old_videos(days: int = 30):
    """
    Очистка старых временных видео файлов.

    Args:
        days: Удалить файлы старше N дней
    """
    import time
    from datetime import datetime, timedelta

    media_dir = Path(settings.MEDIA_LOCAL_DIR)
    cutoff_time = time.time() - (days * 86400)

    deleted_count = 0
    for video_file in media_dir.rglob("*_transcoded.mp4"):
        if video_file.stat().st_mtime < cutoff_time:
            video_file.unlink()
            deleted_count += 1
            logger.info(f"Deleted old video: {video_file}")

    logger.info(f"Cleanup completed: {deleted_count} files deleted")
    return {"deleted_count": deleted_count}
