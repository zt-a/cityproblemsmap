# app/services/media.py
import io
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fastapi import HTTPException, UploadFile, status
from app.config import settings


def validate_file(file: UploadFile, file_bytes: bytes) -> str:
    """
    Проверяет тип и размер.
    Разные лимиты для фото и видео.
    Возвращает 'photo' или 'video'.
    """
    allowed_images = settings.ALLOWED_IMAGE_TYPES.split(",")
    allowed_videos = settings.ALLOWED_VIDEO_TYPES.split(",")
    content_type   = file.content_type or ""

    if content_type not in allowed_images + allowed_videos:
        raise HTTPException(
            status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail      = f"Неподдерживаемый тип: {content_type}",
        )

    is_photo   = content_type in allowed_images
    max_mb     = settings.MAX_IMAGE_SIZE_MB if is_photo else settings.MAX_VIDEO_SIZE_MB
    max_bytes  = max_mb * 1024 * 1024

    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail      = f"Файл слишком большой. "
                          f"Максимум для {'фото' if is_photo else 'видео'}: {max_mb}MB",
        )

    return "photo" if is_photo else "video"


def extract_exif(file_bytes: bytes) -> dict:
    """Извлекает GPS и время съёмки из EXIF."""
    result = {"exif_lat": None, "exif_lon": None, "exif_taken_at": None}

    try:
        image    = Image.open(io.BytesIO(file_bytes))
        exif_raw = image._getexif()
        if not exif_raw:
            return result

        exif = {TAGS.get(k, k): v for k, v in exif_raw.items()}

        if "DateTimeOriginal" in exif:
            try:
                result["exif_taken_at"] = datetime.strptime(
                    exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S"
                )
            except ValueError:
                pass

        if "GPSInfo" in exif:
            gps = {GPSTAGS.get(k, k): v for k, v in exif["GPSInfo"].items()}
            lat = _parse_gps(gps, "Latitude",  "LatitudeRef")
            lon = _parse_gps(gps, "Longitude", "LongitudeRef")
            if lat and lon:
                result["exif_lat"] = round(lat, 6)
                result["exif_lon"] = round(lon, 6)

    except Exception:
        pass

    return result


def _parse_gps(gps: dict, coord: str, ref: str):
    if coord not in gps:
        return None
    try:
        d, m, s   = float(gps[coord][0]), float(gps[coord][1]), float(gps[coord][2])
        decimal   = d + m / 60 + s / 3600
        if gps.get(ref, "") in ("S", "W"):
            decimal = -decimal
        return decimal
    except Exception:
        return None


def verify_geo_match(
    exif_lat: float | None, exif_lon: float | None,
    problem_lat: float, problem_lon: float,
    max_distance_m: int = 1000,
) -> bool:
    if exif_lat is None or exif_lon is None:
        return True

    import math
    R    = 6371000
    lat1 = math.radians(exif_lat)
    lat2 = math.radians(problem_lat)
    dlat = math.radians(problem_lat - exif_lat)
    dlon = math.radians(problem_lon - exif_lon)
    a    = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return dist <= max_distance_m