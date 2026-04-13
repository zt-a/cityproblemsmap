# app/models/zone.py
from sqlalchemy import Column, Integer, String, Float, JSON
from geoalchemy2 import Geometry
from app.database import Base
from app.models.mixins import VersionMixin


class Zone(VersionMixin, Base):
    __tablename__ = "zones"

    name             = Column(String(200), nullable=False)
    zone_type        = Column(String(50),  nullable=False)  # country/city/district/neighborhood
    parent_entity_id = Column(Integer,     nullable=True)

    country          = Column(String(100), nullable=True)
    city             = Column(String(100), nullable=True)

    boundary = Column(Geometry("POLYGON", srid=4326, spatial_index=False), nullable=True)
    center_lat       = Column(Float, nullable=True)
    center_lon       = Column(Float, nullable=True)

    total_problems   = Column(Integer, default=0)
    open_problems    = Column(Integer, default=0)
    solved_problems  = Column(Integer, default=0)
    pollution_index  = Column(Float, default=0.0)
    traffic_index    = Column(Float, default=0.0)
    risk_score       = Column(Float, default=0.0)

    extra_data       = Column(JSON, nullable=True)