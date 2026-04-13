# app/models/user.py
import enum
from sqlalchemy import Column, String, Boolean, Float, Enum, Text, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import VersionMixin


class UserRole(str, enum.Enum):
    user      = "user"
    moderator = "moderator"
    admin     = "admin"
    official  = "official"
    volunteer = "volunteer"


class UserStatus(str, enum.Enum):
    active      = "active"
    suspended   = "suspended"
    deactivated = "deactivated"


class User(VersionMixin, Base):
    __tablename__ = "users"

    username        = Column(String(64),  nullable=False, index=True)
    email           = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole),   default=UserRole.user,       nullable=False)
    status          = Column(Enum(UserStatus), default=UserStatus.active,   nullable=False)

    country         = Column(String(100), nullable=True)
    city            = Column(String(100), nullable=True)
    district        = Column(String(100), nullable=True)

    reputation      = Column(Float,   default=0.0,  nullable=False)
    is_verified     = Column(Boolean, default=False, nullable=False)

    # Ban fields
    is_banned           = Column(Boolean, default=False, nullable=False)
    ban_reason          = Column(Text, nullable=True)
    ban_until           = Column(DateTime, nullable=True)
    banned_by_entity_id = Column(Integer, nullable=True)
    banned_at           = Column(DateTime, nullable=True)

    # 2FA fields
    totp_enabled        = Column(Boolean, default=False, nullable=False)
    totp_secret         = Column(String(32), nullable=True)
    backup_codes        = Column(JSON, nullable=True)