# app/models/comment.py
from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import VersionMixin


class Comment(VersionMixin, Base):
    __tablename__ = "comments"

    problem_entity_id = Column(Integer, nullable=False, index=True)
    author_entity_id  = Column(Integer, nullable=False, index=True)
    parent_entity_id  = Column(Integer, nullable=True)  # вложенность

    content           = Column(Text,        nullable=False)
    comment_type      = Column(String(50),  default="user")
    # user / official_response / resolver_update / system

    is_flagged        = Column(Boolean,     default=False)
    flag_reason       = Column(String(200), nullable=True)
    sentiment_score   = Column(Float,       nullable=True)  # NLP (будущее)