# app/utils/pagination.py
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
import base64
import json

T = TypeVar('T')


class CursorPage(BaseModel, Generic[T]):
    """Ответ с cursor-based пагинацией"""
    items: list[T]
    next_cursor: Optional[str] = None
    has_more: bool = False
    total: Optional[int] = None  # Опционально, может быть дорого считать


def encode_cursor(data: dict) -> str:
    """Кодирует данные курсора в base64 строку"""
    json_str = json.dumps(data, default=str)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> dict:
    """Декодирует курсор из base64 строки"""
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return {}


def create_cursor(last_item, sort_field: str = "created_at") -> str:
    """
    Создает курсор на основе последнего элемента.

    Args:
        last_item: Последний элемент в текущей странице
        sort_field: Поле для сортировки (по умолчанию created_at)

    Returns:
        Закодированный курсор
    """
    cursor_data = {
        "id": last_item.id if hasattr(last_item, "id") else last_item.entity_id,
        sort_field: str(getattr(last_item, sort_field)),
    }
    return encode_cursor(cursor_data)


def parse_cursor_filters(cursor: Optional[str], sort_field: str = "created_at") -> dict:
    """
    Парсит курсор и возвращает фильтры для SQL запроса.

    Args:
        cursor: Закодированный курсор
        sort_field: Поле для сортировки

    Returns:
        Словарь с данными курсора
    """
    if not cursor:
        return {}

    return decode_cursor(cursor)
