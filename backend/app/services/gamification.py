# app/services/gamification.py
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.gamification import (
    Achievement,
    UserAchievement,
    UserLevel,
    Challenge,
    UserChallenge,
)
from app.models.problem import Problem
from app.models.vote import Vote
from app.models.comment import Comment
from app.models.user import User


class GamificationService:
    """Сервис геймификации"""

    # XP за действия
    XP_REWARDS = {
        "create_problem": 10,
        "solve_problem": 50,
        "vote": 1,
        "comment": 5,
        "verified_problem": 20,
        "helpful_comment": 10,
    }

    # Уровни и требуемый XP
    LEVEL_XP = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000,
        6: 2000,
        7: 4000,
        8: 8000,
        9: 15000,
        10: 30000,
    }

    @staticmethod
    def award_xp(db: Session, user_entity_id: int, amount: int, action: str = "manual"):
        """Начислить XP пользователю"""
        if amount is None:
            amount = GamificationService.XP_REWARDS.get(action, 0)

        # Получить или создать уровень пользователя
        user_level = (
            db.query(UserLevel)
            .filter_by(user_entity_id=user_entity_id, is_current=True)
            .first()
        )

        if not user_level:
            entity_id = UserLevel.next_entity_id(db)
            user_level = UserLevel(
                entity_id=entity_id,
                version=1,
                is_current=True,
                user_entity_id=user_entity_id,
                level=1,
                xp=0,
                next_level_xp=100,
                changed_by_id=user_entity_id,
            )
            db.add(user_level)
            db.flush()

        # Добавить XP
        new_xp = user_level.xp + amount

        # Проверить повышение уровня
        new_level = user_level.level
        for level, required_xp in sorted(GamificationService.LEVEL_XP.items()):
            if new_xp >= required_xp:
                new_level = level

        # Обновить уровень
        if new_level > user_level.level or new_xp != user_level.xp:
            user_level.is_current = False
            user_level.superseded_at = datetime.now(timezone.utc)

            next_level_xp = GamificationService.LEVEL_XP.get(new_level + 1, new_xp + 1000)

            new_user_level = UserLevel(
                entity_id=user_level.entity_id,
                version=user_level.version + 1,
                is_current=True,
                user_entity_id=user_entity_id,
                level=new_level,
                xp=new_xp,
                next_level_xp=next_level_xp,
                title=GamificationService._get_title(new_level),
                changed_by_id=user_entity_id,
                change_reason=f"xp_awarded_{action}",
            )
            db.add(new_user_level)

        db.commit()
        return new_level > user_level.level  # True если повысился уровень

    @staticmethod
    def _get_title(level: int) -> str:
        """Получить звание по уровню"""
        titles = {
            1: "Новичок",
            2: "Активист",
            3: "Волонтёр",
            4: "Эксперт",
            5: "Мастер",
            6: "Гуру",
            7: "Легенда",
            8: "Герой города",
            9: "Защитник",
            10: "Хранитель",
        }
        return titles.get(level, f"Уровень {level}")

    @staticmethod
    def check_achievements(db: Session, user_entity_id: int):
        """Проверить и выдать достижения пользователю"""
        # Получить статистику пользователя
        problems_count = (
            db.query(Problem)
            .filter_by(author_entity_id=user_entity_id, version=1)
            .count()
        )

        votes_count = (
            db.query(Vote)
            .filter_by(user_entity_id=user_entity_id, version=1)
            .count()
        )

        comments_count = (
            db.query(Comment)
            .filter_by(author_entity_id=user_entity_id, version=1)
            .count()
        )

        solved_count = (
            db.query(Problem)
            .filter_by(
                author_entity_id=user_entity_id,
                status="solved",
                is_current=True,
            )
            .count()
        )

        # Проверить достижения
        achievements_to_award = []

        if problems_count >= 1:
            achievements_to_award.append("first_problem")
        if problems_count >= 10:
            achievements_to_award.append("10_problems")
        if problems_count >= 50:
            achievements_to_award.append("50_problems")
        if problems_count >= 100:
            achievements_to_award.append("100_problems")

        if solved_count >= 10:
            achievements_to_award.append("10_solved")
        if solved_count >= 50:
            achievements_to_award.append("50_solved")

        if votes_count >= 100:
            achievements_to_award.append("active_citizen")

        if comments_count >= 50:
            achievements_to_award.append("commentator")

        # Выдать достижения
        for achievement_code in achievements_to_award:
            existing = (
                db.query(UserAchievement)
                .filter_by(
                    user_entity_id=user_entity_id,
                    achievement_code=achievement_code,
                    is_current=True,
                )
                .first()
            )

            if not existing:
                entity_id = UserAchievement.next_entity_id(db)
                user_achievement = UserAchievement(
                    entity_id=entity_id,
                    version=1,
                    is_current=True,
                    user_entity_id=user_entity_id,
                    achievement_code=achievement_code,
                    earned_at=datetime.now(timezone.utc),
                    changed_by_id=user_entity_id,
                )
                db.add(user_achievement)

        db.commit()

    @staticmethod
    def get_user_stats(db: Session, user_entity_id: int) -> dict:
        """Получить статистику пользователя для геймификации"""
        user_level = (
            db.query(UserLevel)
            .filter_by(user_entity_id=user_entity_id, is_current=True)
            .first()
        )

        achievements = (
            db.query(UserAchievement)
            .filter_by(user_entity_id=user_entity_id, is_current=True)
            .all()
        )

        return {
            "level": user_level.level if user_level else 1,
            "xp": user_level.xp if user_level else 0,
            "next_level_xp": user_level.next_level_xp if user_level else 100,
            "title": user_level.title if user_level else "Новичок",
            "achievements_count": len(achievements),
            "achievements": [a.achievement_code for a in achievements],
        }
