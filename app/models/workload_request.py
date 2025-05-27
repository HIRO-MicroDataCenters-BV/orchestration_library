"""
SQLAlchemy models for the orchestration library.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    UUID
)

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class WorkloadRequest(Base, BaseDictMixin):
    """
    Model representing a workload request.
    """
    __tablename__ = "workload_request"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    api_version = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    status = Column(String(100), nullable=True)
    current_scale = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
