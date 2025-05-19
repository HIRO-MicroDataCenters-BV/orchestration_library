"""
SQLAlchemy models for the orchestration library.
"""

# pylint: disable=too-few-public-methods

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
)

from app.db.database import Base

class WorkloadRequest(Base):
    """
    Model representing a workload request.
    """
    __tablename__ = "workload_request"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    api_version = Column(String(50), nullable=False)
    kind = Column(String(50), nullable=False)
    current_scale = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
