# app/schemas/media.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.media import MediaType, MediaStatus, MediaCategory


class MediaPublic(BaseModel):
    """Публичные данные медиафайла."""
    entity_id:          int
    version:            int
    problem_entity_id:  int
    uploader_entity_id: int
    media_type:         MediaType
    media_category:     MediaCategory
    status:             MediaStatus
    url:                str
    thumbnail_url:      str | None
    file_size:          int | None
    caption:            str | None
    display_order:      int
    duration_seconds:   int | None
    video_width:        int | None
    video_height:       int | None
    is_processed:       int
    hls_url:            str | None
    exif_lat:           float | None
    exif_lon:           float | None
    exif_taken_at:      datetime | None
    ai_tags:            str | None
    is_current:         bool
    created_at:         datetime

    model_config = {"from_attributes": True}


class MediaUpdate(BaseModel):
    """Схема для обновления медиа (замена файла или изменение caption)."""
    caption: str | None = Field(None, max_length=500, description="Подпись к медиа")


class MediaReorder(BaseModel):
    """Схема для изменения порядка отображения медиа."""
    media_order: list[int] = Field(..., description="Список entity_id в нужном порядке")
