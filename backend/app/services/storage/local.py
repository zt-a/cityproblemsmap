# app/services/storage/local.py
from pathlib import Path
from app.services.storage.base import BaseStorage
from app.config import settings


class LocalStorage(BaseStorage):
    """
    Хранит файлы локально на диске.
    Используется во время разработки.

    Структура папок:
    media/
      problems/
        {problem_entity_id}/
          photo_{entity_id}.jpg
          video_{entity_id}.mp4
    """

    def __init__(self):
        self.base_dir = Path(settings.MEDIA_LOCAL_DIR)
        self.base_url = settings.MEDIA_BASE_URL

    def _get_dir(self, problem_entity_id: int) -> Path:
        """Создаёт папку для проблемы если не существует."""
        path = self.base_dir / "problems" / str(problem_entity_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def upload(
        self,
        file_bytes:        bytes,
        entity_id:         int,
        problem_entity_id: int,
        media_type:        str,
        content_type:      str,
    ) -> dict:
        # Определяем расширение из content_type
        ext_map = {
            "image/jpeg":     "jpg",
            "image/png":      "png",
            "image/webp":     "webp",
            "video/mp4":      "mp4",
            "video/quicktime": "mov",
            "video/avi":      "avi",
        }
        ext = ext_map.get(content_type, "bin")

        prefix    = "photo" if media_type == "photo" else "video"
        filename  = f"{prefix}_{entity_id}.{ext}"
        directory = self._get_dir(problem_entity_id)
        filepath  = directory / filename

        # Сохраняем файл
        with open(filepath, "wb") as f:
            f.write(file_bytes)

        # Строим URL для доступа через FastAPI static files
        relative  = f"problems/{problem_entity_id}/{filename}"
        url       = f"{self.base_url}/{relative}"
        storage_key = str(filepath)

        # Thumbnail для фото — уменьшенная копия
        thumbnail_url = None
        if media_type == "photo":
            thumbnail_url = self._create_thumbnail(
                file_bytes, entity_id, problem_entity_id, ext
            )

        return {
            "url":           url,
            "thumbnail_url": thumbnail_url,
            "file_size":     len(file_bytes),
            "storage_key":   storage_key,
            "local_path":    str(filepath),  # Для обработки видео
        }

    def _create_thumbnail(
        self,
        file_bytes:        bytes,
        entity_id:         int,
        problem_entity_id: int,
        ext:               str,
    ) -> str | None:
        """Создаёт thumbnail 400x300 для фото через Pillow."""
        try:
            import io
            from PIL import Image

            image = Image.open(io.BytesIO(file_bytes))
            image.thumbnail((400, 300))

            # Конвертируем RGBA в RGB если нужно (для JPEG)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            thumb_filename = f"thumb_{entity_id}.jpg"
            directory      = self._get_dir(problem_entity_id)
            thumb_path     = directory / thumb_filename

            image.save(thumb_path, "JPEG", quality=85)

            relative = f"problems/{problem_entity_id}/{thumb_filename}"
            return f"{self.base_url}/{relative}"

        except Exception:
            return None

    def delete(self, storage_key: str, media_type: str = "image") -> None:
        """Удаляет файл с диска."""
        try:
            path = Path(storage_key)
            if path.exists():
                path.unlink()
        except Exception:
            pass