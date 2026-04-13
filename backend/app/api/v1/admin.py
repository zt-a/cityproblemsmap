# app/api/v1/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.problem import Problem, ProblemStatus
from app.models.vote import Vote
from app.models.comment import Comment
from app.models.media import ProblemMedia
from app.schemas.admin import (
    UserAdminView, UserList, ChangeRoleRequest,
    SuspendRequest, SystemStats, RejectProblemRequest,
)
from app.schemas.problem import ProblemPublic, ProblemList
from app.services.versioning import create_new_version
from app.api.deps import get_moderator, get_admin
from app.api.v1.problems import _to_public

router = APIRouter(prefix="/admin", tags=["admin"])


# ══════════════════════════════════════════════════════════
# ПОЛЬЗОВАТЕЛИ
# ══════════════════════════════════════════════════════════

@router.get("/users", response_model=UserList)
def list_users(
    role:         UserRole | None   = Query(None),
    status:       UserStatus | None = Query(None),
    city:         str | None        = Query(None),
    search:       str | None        = Query(None, description="Поиск по username или email"),
    offset:       int               = Query(0,  ge=0),
    limit:        int               = Query(20, ge=1, le=100),
    db:           Session           = Depends(get_db),
    current_user: User              = Depends(get_moderator),
):
    """
    Список всех пользователей.
    Доступно: moderator, official, admin.

    Фильтры: роль, статус, город, поиск по username/email.
    """
    query = db.query(User).filter_by(is_current=True)

    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if city:
        query = query.filter(User.city == city)
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    total = query.count()
    users = (
        query
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return UserList(items=users, total=total, offset=offset, limit=limit)


@router.get("/users/{entity_id}", response_model=UserAdminView)
def get_user_admin(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Детальный профиль пользователя для модерации.
    Включает email и полный статус.
    """
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.patch("/users/{entity_id}/role", response_model=UserAdminView)
def change_user_role(
    entity_id:    int,
    data:         ChangeRoleRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_admin),
):
    """
    Смена роли пользователя.
    Только admin.

    Нельзя менять роль самому себе —
    защита от случайного снятия прав.
    """
    if entity_id == current_user.entity_id:
        raise HTTPException(
            status_code = 400,
            detail      = "Нельзя менять роль самому себе",
        )

    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.role == data.role:
        raise HTTPException(
            status_code = 400,
            detail      = f"Пользователь уже имеет роль {data.role.value}",
        )

    updated = create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"role_change_to_{data.role.value}",
        role          = data.role,
    )
    return updated


@router.patch("/users/{entity_id}/suspend", response_model=UserAdminView)
def suspend_user(
    entity_id:    int,
    data:         SuspendRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Блокировка пользователя.
    Доступно: moderator, admin.

    Модератор не может заблокировать админа или другого модератора.
    """
    if entity_id == current_user.entity_id:
        raise HTTPException(
            status_code = 400,
            detail      = "Нельзя заблокировать самого себя",
        )

    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.status == UserStatus.suspended:
        raise HTTPException(
            status_code = 400,
            detail      = "Пользователь уже заблокирован",
        )

    # Модератор не может блокировать привилегированных
    privileged_roles = {UserRole.admin, UserRole.moderator, UserRole.official}
    if (
        current_user.role == UserRole.moderator
        and user.role in privileged_roles
    ):
        raise HTTPException(
            status_code = 403,
            detail      = "Модератор не может блокировать admin/moderator/official",
        )

    updated = create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = f"suspended: {data.reason}",
        status        = UserStatus.suspended,
    )
    return updated


@router.patch("/users/{entity_id}/unsuspend", response_model=UserAdminView)
def unsuspend_user(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """Снятие блокировки пользователя."""
    user = (
        db.query(User)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.status != UserStatus.suspended:
        raise HTTPException(
            status_code = 400,
            detail      = "Пользователь не заблокирован",
        )

    updated = create_new_version(
        db            = db,
        model_class   = User,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "unsuspended",
        status        = UserStatus.active,
    )
    return updated


@router.get("/users/{entity_id}/history", response_model=list[UserAdminView])
def get_user_history(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_admin),
):
    """
    Полная история версий пользователя.
    Только admin — видит все изменения профиля.
    """
    versions = (
        db.query(User)
        .filter_by(entity_id=entity_id)
        .order_by(User.version.asc())
        .all()
    )
    if not versions:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return versions


# ══════════════════════════════════════════════════════════
# ПРОБЛЕМЫ
# ══════════════════════════════════════════════════════════

@router.get("/problems", response_model=ProblemList)
def list_problems_admin(
    status:       ProblemStatus | None = Query(None),
    city:         str | None           = Query(None),
    problem_type: str | None           = Query(None),
    author_id:    int | None           = Query(None),
    offset:       int                  = Query(0,  ge=0),
    limit:        int                  = Query(20, ge=1, le=100),
    db:           Session              = Depends(get_db),
    current_user: User                 = Depends(get_moderator),
):
    """
    Все проблемы включая rejected и archived.
    Доступно: moderator, official, admin.
    """
    query = db.query(Problem).filter_by(is_current=True)

    if status:
        query = query.filter(Problem.status == status)
    if city:
        query = query.filter(Problem.city == city)
    if problem_type:
        query = query.filter(Problem.problem_type == problem_type)
    if author_id:
        query = query.filter(Problem.author_entity_id == author_id)

    total    = query.count()
    problems = (
        query
        .order_by(Problem.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ProblemList(
        items  = [_to_public(p) for p in problems],
        total  = total,
        offset = offset,
        limit  = limit,
    )


@router.patch("/problems/{entity_id}/reject", response_model=ProblemPublic)
def reject_problem(
    entity_id:    int,
    data:         RejectProblemRequest,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_moderator),
):
    """
    Отклонить проблему — статус rejected.
    Доступно: moderator, official, admin.

    Используется когда проблема нарушает правила
    или является заведомо ложной.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    if problem.status == ProblemStatus.rejected:
        raise HTTPException(
            status_code = 400,
            detail      = "Проблема уже отклонена",
        )

    updated = create_new_version(
        db              = db,
        model_class     = Problem,
        entity_id       = entity_id,
        changed_by_id   = current_user.entity_id,
        change_reason   = f"rejected_by_moderator: {data.reason}",
        status          = ProblemStatus.rejected,
        resolution_note = data.reason,
    )
    return _to_public(updated)


@router.patch("/problems/{entity_id}/restore", response_model=ProblemPublic)
def restore_problem(
    entity_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_admin),
):
    """
    Восстановить отклонённую проблему — статус open.
    Только admin.
    """
    problem = (
        db.query(Problem)
        .filter_by(entity_id=entity_id, is_current=True)
        .first()
    )
    if not problem:
        raise HTTPException(status_code=404, detail="Проблема не найдена")

    if problem.status != ProblemStatus.rejected:
        raise HTTPException(
            status_code = 400,
            detail      = "Можно восстановить только отклонённую проблему",
        )

    updated = create_new_version(
        db            = db,
        model_class   = Problem,
        entity_id     = entity_id,
        changed_by_id = current_user.entity_id,
        change_reason = "restored_by_admin",
        status        = ProblemStatus.open,
        resolution_note = None,
    )
    return _to_public(updated)


# ══════════════════════════════════════════════════════════
# СТАТИСТИКА СИСТЕМЫ
# ══════════════════════════════════════════════════════════

@router.get("/stats", response_model=SystemStats)
def get_system_stats(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_admin),
):
    """
    Общая статистика системы.
    Только admin.
    """
    # Пользователи
    total_users     = db.query(User).filter_by(is_current=True).count()
    active_users    = db.query(User).filter_by(is_current=True, status=UserStatus.active).count()
    suspended_users = db.query(User).filter_by(is_current=True, status=UserStatus.suspended).count()

    # Проблемы
    total_problems    = db.query(Problem).filter_by(is_current=True).count()
    open_problems     = db.query(Problem).filter_by(is_current=True, status=ProblemStatus.open).count()
    solved_problems   = db.query(Problem).filter_by(is_current=True, status=ProblemStatus.solved).count()
    rejected_problems = db.query(Problem).filter_by(is_current=True, status=ProblemStatus.rejected).count()

    # Активность
    total_votes    = db.query(Vote).filter_by(is_current=True).count()
    total_comments = db.query(Comment).filter_by(is_current=True).count()
    total_media    = db.query(ProblemMedia).filter_by(is_current=True).count()

    # Уникальные города
    cities_covered = (
        db.query(func.count(func.distinct(Problem.city)))
        .filter_by(is_current=True)
        .scalar() or 0
    )

    return SystemStats(
        total_users       = total_users,
        active_users      = active_users,
        suspended_users   = suspended_users,
        total_problems    = total_problems,
        open_problems     = open_problems,
        solved_problems   = solved_problems,
        rejected_problems = rejected_problems,
        total_votes       = total_votes,
        total_comments    = total_comments,
        total_media       = total_media,
        cities_covered    = cities_covered,
    )