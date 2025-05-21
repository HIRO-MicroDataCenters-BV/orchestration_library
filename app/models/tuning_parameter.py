from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    text,
    Float
)

from app.db.database import Base


class TuningParameter(Base):
    """
    Model representing tuning parameters for the system.
    """
    __tablename__ = "tuning_parameters"

    id = Column(Integer, primary_key=True, index=True)
    output_1 = Column(Float, nullable=False)
    output_2 = Column(Float, nullable=False)
    output_3 = Column(Float, nullable=False)
    alpha = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    gamma = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))