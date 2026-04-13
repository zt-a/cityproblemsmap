# app/services/comments.py
from app.models.comment import Comment
from app.schemas.comment import CommentTree


def build_comment_tree(comments: list[Comment]) -> list[CommentTree]:
    """
    Превращает плоский список комментариев в дерево.

    Вход:  [c1(parent=None), c2(parent=c1), c3(parent=c1), c4(parent=c2)]
    Выход: [c1(replies=[c2(replies=[c4]), c3])]

    Алгоритм:
    1. Сложить все комментарии в словарь entity_id → CommentTree
    2. Пройтись по всем — если есть parent, добавить в replies родителя
    3. Вернуть только корневые (parent_entity_id=None)
    """

    # Словарь для быстрого доступа по entity_id
    lookup: dict[int, CommentTree] = {}
    for c in comments:
        lookup[c.entity_id] = CommentTree(
            entity_id         = c.entity_id,
            version           = c.version,
            problem_entity_id = c.problem_entity_id,
            author_entity_id  = c.author_entity_id,
            parent_entity_id  = c.parent_entity_id,
            content           = c.content,
            comment_type      = c.comment_type,
            is_flagged        = c.is_flagged,
            is_current        = c.is_current,
            created_at        = c.created_at,
            replies           = [],
        )

    roots: list[CommentTree] = []

    for c in comments:
        node = lookup[c.entity_id]
        if c.parent_entity_id is None:
            # Корневой комментарий
            roots.append(node)
        else:
            # Ответ — добавить в replies родителя
            parent = lookup.get(c.parent_entity_id)
            if parent:
                parent.replies.append(node)

    return roots


def increment_comment_count(
    db,
    problem_entity_id: int,
    changed_by_id: int,
    delta: int = 1,         # +1 при добавлении, -1 не используем (soft delete)
) -> None:
    """
    Увеличивает comment_count проблемы через новую версию.
    Вызывается после каждого нового комментария.
    """
    from app.models.problem import Problem
    from app.services.versioning import create_new_version

    problem = (
        db.query(Problem)
        .filter_by(entity_id=problem_entity_id, is_current=True)
        .first()
    )
    if not problem:
        return

    create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = problem_entity_id,
        changed_by_id = changed_by_id,
        change_reason = "comment_count_update",
        comment_count = problem.comment_count + delta,
    )
    db.commit()