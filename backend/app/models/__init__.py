# app/models/__init__.py
# Импортируем все модели чтобы Alembic их видел при генерации миграций
from app.models.user       import User  # noqa: F401
from app.models.zone       import Zone  # noqa: F401
from app.models.problem    import Problem  # noqa: F401
from app.models.media      import ProblemMedia  # noqa: F401
from app.models.vote       import Vote  # noqa: F401
from app.models.comment    import Comment  # noqa: F401
from app.models.simulation import SimulationEvent  # noqa: F401
from app.models.reputation import ReputationLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.user_settings import UserNotificationSettings  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.activity import Activity  # noqa: F401
from app.models.fundraising import Fundraising, Donation, FundraisingExpense  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.gamification import Achievement, UserAchievement, UserLevel, Challenge, UserChallenge  # noqa: F401
from app.models.social import UserProfile, Follow  # noqa: F401