"""
SQLAlchemy models for the placement decision
"""
import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class PlacementDecision(Base, BaseDictMixin):
    __tablename__ = "placement_decision"

    decision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    namespace = Column(String, nullable=False, index=True)

    # Store application spec as JSONB for better query support
    spec = Column(JSONB, nullable=False)

    # Store placements as ARRAY of strings
    decision_placement_lst = Column(ARRAY(String), nullable=False)

    decision_reason = Column(String, nullable=False)
    trace = Column(Text, nullable=True)

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
