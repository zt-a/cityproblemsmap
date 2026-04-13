# app/models/media.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON
from app.database import Base
from app.models.mixins import VersionMixin


class MediaType(str, enum.Enum):
    photo = "photo"
    video = "video"


class MediaStatus(str, enum.Enum):
    active   = "active"
    removed  = "removed"
    replaced = "replaced"


class MediaCategory(str, enum.Enum):
    """
    Категория медиа по этапу решения проблемы:
    - problem: Исходная проблема (фото/видео проблемы)
    - in_progress: Процесс работы (фото/видео во время решения)
    - result: Результат работы (фото/видео после решения)
    """
    problem     = "problem"
    in_progress = "in_progress"
    result      = "result"


class ProblemMedia(VersionMixin, Base):
    __tablename__ = "problem_media"

    problem_entity_id  = Column(Integer, nullable=False, index=True)
    uploader_entity_id = Column(Integer, nullable=False)

    media_type         = Column(Enum(MediaType),     nullable=False)
    media_category     = Column(Enum(MediaCategory), default=MediaCategory.problem)
    status             = Column(Enum(MediaStatus),   default=MediaStatus.active)

    url                = Column(String(500), nullable=False)
    thumbnail_url      = Column(String(500), nullable=True)
    file_size          = Column(Integer,     nullable=True)

    # Описание и порядок отображения
    caption            = Column(String(500), nullable=True)
    display_order      = Column(Integer,     default=0)

    # Метаданные видео
    duration_seconds   = Column(Integer,     nullable=True)
    video_width        = Column(Integer,     nullable=True)
    video_height       = Column(Integer,     nullable=True)
    is_processed       = Column(Integer,     default=0)  # 0=pending, 1=done, 2=failed
    hls_url            = Column(String(500), nullable=True)

    exif_lat           = Column(Float,    nullable=True)
    exif_lon           = Column(Float,    nullable=True)
    exif_taken_at      = Column(DateTime, nullable=True)

    ai_tags            = Column(String(500), nullable=True)
    ai_confidence      = Column(Float,       nullable=True)
    ai_metadata        = Column(JSON,        nullable=True)