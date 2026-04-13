# app/services/storage/__init__.py
from app.config import settings
from app.services.storage.base import BaseStorage


def get_storage() -> BaseStorage:
    """
    Фабрика — возвращает нужный бэкенд по настройке MEDIA_STORAGE.

    Использование:
        storage = get_storage()
        result  = storage.upload(file_bytes, ...)
    """
    if settings.MEDIA_STORAGE == "cloudinary":
        from app.services.storage.cloudinary_storage import CloudinaryStorage
        return CloudinaryStorage()
    else:
        from app.services.storage.local import LocalStorage
        return LocalStorage()