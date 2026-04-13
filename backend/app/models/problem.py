# app/models/problem.py
import enum
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
from app.models.mixins import VersionMixin


class ProblemType(str, enum.Enum):
    pothole       = "pothole"
    garbage       = "garbage"
    road_work     = "road_work"
    pollution     = "pollution"
    traffic_light = "traffic_light"
    flooding      = "flooding"
    lighting      = "lighting"
    construction  = "construction"
    roads         = "roads"
    infrastructure = "infrastructure"
    other         = "other"


class ProblemNature(str, enum.Enum):
    temporary = "temporary"
    permanent = "permanent"


class ProblemStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    solved      = "solved"
    rejected    = "rejected"
    archived    = "archived"


class ResolverType(str, enum.Enum):
    volunteer     = "volunteer"
    official_org  = "official_org"
    auto_resolved = "auto_resolved"


class Problem(VersionMixin, Base):
    __tablename__ = "problems"

    author_entity_id      = Column(Integer, nullable=False, index=True)
    zone_entity_id        = Column(Integer, nullable=True,  index=True)

    title                 = Column(String(300), nullable=False)
    description           = Column(Text,        nullable=True)

    country               = Column(String(100), nullable=False)
    city                  = Column(String(100), nullable=False)
    district              = Column(String(100), nullable=True)
    address               = Column(String(300), nullable=True)
    location = Column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)

    problem_type          = Column(Enum(ProblemType),   nullable=False)
    nature                = Column(Enum(ProblemNature), nullable=False)
    status                = Column(Enum(ProblemStatus), default=ProblemStatus.open)

    resolved_by_entity_id = Column(Integer,          nullable=True)
    resolver_type         = Column(Enum(ResolverType), nullable=True)
    resolved_at           = Column(DateTime,           nullable=True)
    resolution_note       = Column(Text,               nullable=True)

    truth_score           = Column(Float, default=0.0)
    urgency_score         = Column(Float, default=0.0)
    impact_score          = Column(Float, default=0.0)
    inconvenience_score   = Column(Float, default=0.0)
    priority_score        = Column(Float, default=0.0)

    vote_count            = Column(Integer, default=0)
    comment_count         = Column(Integer, default=0)

    tags                  = Column(JSON, nullable=True)
    ai_metadata           = Column(JSON, nullable=True)