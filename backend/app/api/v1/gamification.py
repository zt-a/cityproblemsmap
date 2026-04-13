# app/api/v1/gamification.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.gamification import Achievement, UserAchievement
from app.api.deps import get_current_user
from app.services.gamification import GamificationService
from pydantic import BaseModel, ConfigDict


router = APIRouter(prefix="/gamification", tags=["gamification"])


class UserStatsResponse(BaseModel):
    level: int
    xp: int
    next_level_xp: int
    title: str
    achievements_count: int
    achievements: list[str]


class AchievementResponse(BaseModel):
    code: str
    name: str
    description: str
    icon: str | None
    points: int
    rarity: str
    earned: bool
    earned_at: str | None
    model_config = ConfigDict(from_attributes=True)



@router.get("/stats", response_model=UserStatsResponse)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить статистику геймификации текущего пользователя"""
    stats = GamificationService.get_user_stats(db, current_user.entity_id)
    return stats


@router.get("/achievements", response_model=list[AchievementResponse])
def get_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить все достижения и прогресс пользователя"""
    all_achievements = db.query(Achievement).all()
    user_achievements = (
        db.query(UserAchievement)
        .filter_by(user_entity_id=current_user.entity_id, is_current=True)
        .all()
    )

    earned_codes = {ua.achievement_code: ua.earned_at for ua in user_achievements}

    result = []
    for achievement in all_achievements:
        earned_at = earned_codes.get(achievement.code)
        result.append(
            AchievementResponse(
                code=achievement.code,
                name=achievement.name,
                description=achievement.description,
                icon=achievement.icon,
                points=achievement.points,
                rarity=achievement.rarity,
                earned=achievement.code in earned_codes,
                earned_at=earned_at.isoformat() if earned_at else None,
            )
        )

    return result


@router.post("/check-achievements")
def check_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Проверить и выдать новые достижения"""
    GamificationService.check_achievements(db, current_user.entity_id)
    return {"message": "Achievements checked"}
