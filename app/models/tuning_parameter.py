"""
SQLAlchemy models for tuning parameters.
This module defines the database models used for storing and retrieving tuning parameters.
"""

from sqlalchemy import Column, Integer, TIMESTAMP, text, Float

from app.db.database import Base
from app.models.base_dict_mixin import BaseDictMixin


class TuningParameter(Base, BaseDictMixin):
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
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True
    )

    def get_parameters(self):
        """
        Get the tuning parameters as a dictionary.

        Returns:
            dict: Dictionary containing only the tuning parameters
        """
        return {
            "output_1": self.output_1,
            "output_2": self.output_2,
            "output_3": self.output_3,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
        }

    def __repr__(self):
        """
        String representation of the model instance.

        Returns:
            str: String representation
        """
        return f"<TuningParameter(id={self.id}, created_at={self.created_at})>"
