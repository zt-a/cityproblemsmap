# app/api/v1/comments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.comment import Comment
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.comment import CommentCreate, CommentEdit, CommentPublic, CommentTree
from app.services.versioning import create_new_version
from app.services.comments import build_comment_tree, increment_comment_count
from app.api.deps import get_current_user
from app.utils.pagination import CursorPage, create_cursor, parse_cursor_filters
from app.services.cache import invalidate_problem_cache
from app.middleware.rate_limit import limiter
from app.dependencies.captcha import verify_captcha_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/problems", tags=["comments"])


@router.post("/{problem_entity_id}/comments", response_model=CommentPublic, status_code=201)
@limiter.limit("30/hour")  # 30 комментариев в час - защита от спама
def create_comment(
    request:           Request,
    problem_entity_id: int,
    data:              CommentCreate,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
    captcha_verified:  bool    = Depends(verify_captcha_token)
):
    """
    Добавить комментарий к проблеме.
    Если передан parent_entity_id — это ответ на другой комментарий.
    """

    # Проверить что проблема существует
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    # Если это ответ — проверить что родительский комментарий существует
    # и принадлежит этой же проблеме
    if data.parent_entity_id is not None:
        parent = (
            db.query(Comment)
            .filter_by(
                entity_id         = data.parent_entity_id,
                problem_entity_id = problem_entity_id,
                is_current        = True,
            )
            .first()
        )
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Родительский комментарий не найден",
            )

        # Защита от глубокой вложенности — максимум 1 уровень ответов
        # Ответ на ответ запрещён — упрощает UI и дерево
        if parent.parent_entity_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отвечать на ответ — только на корневой комментарий",
            )

    # Определить тип комментария по роли пользователя
    if current_user.role in (UserRole.official, UserRole.admin):
        comment_type = "official_response"
    else:
        comment_type = "user"

    entity_id = Comment.next_entity_id(db)

    comment = Comment(
        entity_id         = entity_id,
        version           = 1,
        is_current        = True,
        problem_entity_id = problem_entity_id,
        author_entity_id  = current_user.entity_id,
        parent_entity_id  = data.parent_entity_id,
        content           = data.content,
        comment_type      = comment_type,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Увеличить comment_count проблемы — создаёт новую версию проблемы
    increment_comment_count(
        db                = db,
        problem_entity_id = problem_entity_id,
        changed_by_id     = current_user.entity_id,
    )

    # Инвалидируем кеш — comment_count изменился
    invalidate_problem_cache(problem_entity_id)

    # Создать уведомления
    try:
        from app.services.notification_service import NotificationService

        # Если это ответ на комментарий - уведомить автора родительского комментария
        if data.parent_entity_id:
            parent = db.query(Comment).filter_by(
                entity_id=data.parent_entity_id,
                is_current=True
            ).first()
            if parent:
                NotificationService.notify_comment_replied(
                    db=db,
                    parent_comment=parent,
                    reply_comment=comment,
                    actor_entity_id=current_user.entity_id,
                )
        else:
            # Если это комментарий к проблеме - уведомить автора проблемы
            NotificationService.notify_problem_commented(
                db=db,
                problem=problem,
                comment=comment,
                actor_entity_id=current_user.entity_id,
            )
    except Exception as e:
        logger.warning(f"Failed to create notification: {e}")

    # Отправить WebSocket уведомление
    try:
        from app.services.notifications import broadcast_problem_update
        broadcast_problem_update(
            problem_id=problem_entity_id,
            update_type="comment_added",
            data={
                "comment_id": comment.entity_id,
                "author_id": current_user.entity_id,
                "content": comment.content[:100],  # Первые 100 символов
            }
        )
    except Exception as e:
        logger.warning(f"Failed to broadcast comment update: {e}")

    return comment


@router.get("/{problem_entity_id}/comments", response_model=list[CommentTree])
def get_comments(
    problem_entity_id: int,
    db:                Session = Depends(get_db),
):
    """
    Дерево комментариев к проблеме.
    Возвращает только актуальные версии в виде вложенной структуры.

    Пример ответа:
    [
      { entity_id: 1, content: "...", replies: [
          { entity_id: 3, content: "...", replies: [] },
          { entity_id: 4, content: "...", replies: [] },
      ]},
      { entity_id: 2, content: "...", replies: [] },
    ]
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    comments = (
        db.query(Comment)
        .filter_by(problem_entity_id=problem_entity_id, is_current=True)
        .order_by(Comment.created_at.asc())
        .all()
    )

    return build_comment_tree(comments)


@router.get("/{problem_entity_id}/comments/paginated", response_model=CursorPage[CommentPublic])
def get_comments_paginated(
    problem_entity_id: int,
    cursor:            Optional[str] = Query(None, description="Курсор для пагинации"),
    limit:             int = Query(20, ge=1, le=100, description="Количество комментариев"),
    db:                Session = Depends(get_db),
):
    """
    Список комментариев с cursor-based пагинацией.
    Используется для бесконечной прокрутки (infinite scroll).

    Cursor содержит информацию о последнем элементе предыдущей страницы.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    query = (
        db.query(Comment)
        .filter_by(problem_entity_id=problem_entity_id, is_current=True)
    )

    # Применяем курсор если есть
    if cursor:
        cursor_data = parse_cursor_filters(cursor, "created_at")
        if cursor_data:
            # Получаем комментарии после курсора
            query = query.filter(
                Comment.created_at > cursor_data.get("created_at")
            )

    # Получаем limit + 1 для проверки has_more
    comments = (
        query
        .order_by(Comment.created_at.asc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(comments) > limit
    items = comments[:limit]

    next_cursor = None
    if has_more and items:
        next_cursor = create_cursor(items[-1], "created_at")

    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.patch("/{problem_entity_id}/comments/{comment_entity_id}", response_model=CommentPublic)
def edit_comment(
    problem_entity_id: int,
    comment_entity_id: int,
    data:              CommentEdit,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Редактировать свой комментарий.
    Создаёт новую версию — оригинальный текст остаётся в БД.
    """
    comment = (
        db.query(Comment)
        .filter_by(
            entity_id         = comment_entity_id,
            problem_entity_id = problem_entity_id,
            is_current        = True,
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    # Только автор может редактировать
    if comment.author_entity_id != current_user.entity_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно редактировать только свои комментарии",
        )

    updated = create_new_version(
        db            = db,
        model_class   = Comment,
        entity_id     = comment_entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "user_edited",
        content       = data.content,
    )
    return updated


@router.patch("/{problem_entity_id}/comments/{comment_entity_id}/flag", response_model=CommentPublic)
def flag_comment(
    problem_entity_id: int,
    comment_entity_id: int,
    reason:            str,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    Пожаловаться на комментарий (любой пользователь)
    или скрыть его (модератор/админ).

    Обычный пользователь: ставит is_flagged=True, виден модераторам.
    Модератор/админ: дополнительно помечает comment_type='moderated'
    что скрывает комментарий в публичном UI.
    """
    comment = (
        db.query(Comment)
        .filter_by(
            entity_id         = comment_entity_id,
            problem_entity_id = problem_entity_id,
            is_current        = True,
        )
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    is_moderator = current_user.role in (UserRole.admin, UserRole.moderator)

    fields = {
        "is_flagged":  True,
        "flag_reason": reason,
    }

    # Модератор скрывает — меняет тип
    if is_moderator:
        fields["comment_type"] = "moderated"

    updated = create_new_version(
        db            = db,
        model_class   = Comment,
        entity_id     = comment_entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "flagged_by_moderator" if is_moderator else "flagged_by_user",
        **fields,
    )
    return updated


@router.get("/{problem_entity_id}/comments/{comment_entity_id}/history", response_model=list[CommentPublic])
def get_comment_history(
    problem_entity_id: int,
    comment_entity_id: int,
    db:                Session = Depends(get_db),
    current_user:      User    = Depends(get_current_user),
):
    """
    История версий комментария — все редакции.
    Только для модераторов и админов.
    """
    if current_user.role not in (UserRole.admin, UserRole.moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только для модераторов",
        )

    versions = (
        db.query(Comment)
        .filter_by(
            entity_id         = comment_entity_id,
            problem_entity_id = problem_entity_id,
        )
        .order_by(Comment.version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return versions