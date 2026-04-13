# app/services/storage/base.py
from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """
    Абстрактный интерфейс хранилища.
    Любой бэкенд должен реализовать эти методы.
    """

    @abstractmethod
    def upload(
        self,
        file_bytes:        bytes,
        entity_id:         int,
        problem_entity_id: int,
        media_type:        str,    # "photo" или "video"
        content_type:      str,    # "image/jpeg" и т.д.
    ) -> dict:
        """
        Загружает файл.
        Возвращает:
        {
            "url":           str,
            "thumbnail_url": str | None,
            "file_size":     int,
            "storage_key":   str,  # путь или public_id для удаления
        }
        """
        ...

    @abstractmethod
    def delete(self, storage_key: str, media_type: str) -> None:
        """Удаляет файл по ключу."""
        ...