# app/models/user_settings.py
from sqlalchemy import Column, Integer, Boolean, String
from app.models.mixins import VersionMixin
from app.database import Base


class UserNotificationSettings(VersionMixin, Base):
    """Настройки уведомлений пользователя"""
    __tablename__ = "user_notification_settings"

    user_entity_id = Column(Integer, nullable=False, index=True)

    # Email уведомления
    email_enabled = Column(Boolean, nullable=False, default=True)
    email_on_comment = Column(Boolean, nullable=False, default=True)
    email_on_status_change = Column(Boolean, nullable=False, default=True)
    email_on_official_response = Column(Boolean, nullable=False, default=True)
    email_on_problem_solved = Column(Boolean, nullable=False, default=True)
    email_on_mention = Column(Boolean, nullable=False, default=True)

    # Push уведомления (для будущего)
    push_enabled = Column(Boolean, nullable=False, default=True)
    push_on_comment = Column(Boolean, nullable=False, default=True)
    push_on_status_change = Column(Boolean, nullable=False, default=True)

    # Дайджест
    digest_enabled = Column(Boolean, nullable=False, default=True)
    digest_frequency = Column(String(20), nullable=False, default="daily")  # daily/weekly/monthly
    digest_day = Column(Integer, nullable=True)  # День недели для weekly (0-6) или день месяца для monthly

    # Дополнительные настройки
    quiet_hours_enabled = Column(Boolean, nullable=False, default=False)
    quiet_hours_start = Column(Integer, nullable=True)  # Час начала (0-23)
    quiet_hours_end = Column(Integer, nullable=True)  # Час окончания (0-23)

    def __repr__(self):
        return f"<UserNotificationSettings(user={self.user_entity_id}, email={self.email_enabled})>"
