# app/models/simulation.py
import enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, JSON
from geoalchemy2 import Geometry
from app.database import Base
from app.models.mixins import VersionMixin


class SimEventType(str, enum.Enum):
    road_repair            = "road_repair"
    new_construction       = "new_construction"
    demolition             = "demolition"
    flood_risk             = "flood_risk"
    pollution_source       = "pollution_source"
    traffic_change         = "traffic_change"
    infrastructure_upgrade = "infrastructure_upgrade"


class SimEventStatus(str, enum.Enum):
    planned   = "planned"
    active    = "active"
    completed = "completed"
    cancelled = "cancelled"


class SimulationEvent(VersionMixin, Base):
    __tablename__ = "simulation_events"

    zone_entity_id       = Column(Integer, nullable=False, index=True)
    created_by_entity_id = Column(Integer, nullable=False)

    event_type    = Column(Enum(SimEventType),   nullable=False)
    status        = Column(Enum(SimEventStatus), default=SimEventStatus.planned)

    title         = Column(String(300), nullable=False)
    description   = Column(Text,        nullable=True)

    affected_area = Column(Geometry("GEOMETRY", srid=4326, spatial_index=False), nullable=True)

    planned_start  = Column(DateTime, nullable=True)
    planned_end    = Column(DateTime, nullable=True)
    actual_start   = Column(DateTime, nullable=True)
    actual_end     = Column(DateTime, nullable=True)

    traffic_impact   = Column(Float, default=0.0)
    pollution_impact = Column(Float, default=0.0)
    risk_delta       = Column(Float, default=0.0)

    simulation_params = Column(JSON, nullable=True)