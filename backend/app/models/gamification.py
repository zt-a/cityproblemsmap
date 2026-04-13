# app/models/gamification.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.models.mixins import VersionMixin
from app.database import Base


class Achievement(Base):
    """Достижения (badges)"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(200), nullable=True)
    criteria = Column(JSON, nullable=False)  # Условия получения
    points = Column(Integer, nullable=False, default=10)
    rarity = Column(String(20), nullable=False, default="common")  # common/rare/epic/legendary

    def __repr__(self):
        return f"<Achievement(code={self.code}, name={self.name})>"


class UserAchievement(VersionMixin, Base):
    """Достижения пользователей"""
    __tablename__ = "user_achievements"

    user_entity_id = Column(Integer, nullable=False, index=True)
    achievement_code = Column(String(50), nullable=False, index=True)
    earned_at = Column(DateTime, nullable=False)
    progress = Column(JSON, nullable=True)  # Прогресс к достижению

    def __repr__(self):
        return f"<UserAchievement(user={self.user_entity_id}, achievement={self.achievement_code})>"


class UserLevel(VersionMixin, Base):
    """Уровни пользователей"""
    __tablename__ = "user_levels"

    
    user_entity_id = Column(Integer, nullable=False, index=True)
    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    next_level_xp = Column(Integer, nullable=False, default=100)
    title = Column(String(100), nullable=True)  # Звание

    def __repr__(self):
        return f"<UserLevel(user={self.user_entity_id}, level={self.level}, xp={self.xp})>"


class Challenge(Base):
    """Челленджи (месячные задания)"""
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    criteria = Column(JSON, nullable=False)
    reward_xp = Column(Integer, nullable=False, default=100)
    reward_achievement = Column(String(50), nullable=True)
    is_active = Column(Integer, nullable=False, default=True)

    def __repr__(self):
        return f"<Challenge(code={self.code}, name={self.name})>"


class UserChallenge(VersionMixin, Base):
    """Участие пользователей в челленджах"""
    __tablename__ = "user_challenges"

    user_entity_id = Column(Integer, nullable=False, index=True)
    challenge_code = Column(String(50), nullable=False, index=True)
    progress = Column(JSON, nullable=False)  # Текущий прогресс
    completed = Column(Integer, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<UserChallenge(user={self.user_entity_id}, challenge={self.challenge_code})>"
