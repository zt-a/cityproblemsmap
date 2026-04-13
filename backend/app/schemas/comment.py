# app/schemas/comment.py
from pydantic import BaseModel, field_validator
from datetime import datetime


class CommentCreate(BaseModel):
    """Данные для создания комментария."""
    content:         str
    parent_entity_id: int | None = None  # None = корневой, int = ответ на комментарий

    @field_validator("content")
    @classmethod
    def content_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Минимум 2 символа")
        if len(v) > 2000:
            raise ValueError("Максимум 2000 символов")
        return v


class CommentEdit(BaseModel):
    """Редактирование текста комментария — создаёт новую версию."""
    content: str

    @field_validator("content")
    @classmethod
    def content_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Минимум 2 символа")
        if len(v) > 2000:
            raise ValueError("Максимум 2000 символов")
        return v


class CommentPublic(BaseModel):
    """Публичные данные комментария."""
    entity_id:         int
    version:           int
    problem_entity_id: int
    author_entity_id:  int
    parent_entity_id:  int | None
    content:           str
    comment_type:      str
    is_flagged:        bool
    is_current:        bool
    created_at:        datetime

    model_config = {"from_attributes": True}


class CommentTree(BaseModel):
    """
    Комментарий с вложенными ответами.
    Используется для отображения треда на фронте.
    """
    entity_id:         int
    version:           int
    problem_entity_id: int
    author_entity_id:  int
    parent_entity_id:  int | None
    content:           str
    comment_type:      str
    is_flagged:        bool
    is_current:        bool
    created_at:        datetime
    replies:           list["CommentTree"] = []  # вложенные ответы

    model_config = {"from_attributes": True}