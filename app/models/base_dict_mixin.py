"""
# app/models/base_dict_mixin.py
"""
class BaseDictMixin:
    """
    Mixin class to add dictionary serialization capabilities to SQLAlchemy models.
    This mixin provides methods to convert model instances to dictionaries and
    to create model instances from dictionaries.
    """
    def to_dict(self):
        """
        Convert the model instance to a dictionary representation.
        Returns:
            dict: A dictionary representation of the model instance.
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    @classmethod
    def from_dict(cls, data):
        """
        Create a model instance from a dictionary.
        Args:
            data (dict): A dictionary containing the model's field values.
        Returns:
            BaseDictMixin: An instance of the model class populated with the data.
        """
        # Only use keys that are columns in the model
        fields = {col.name for col in cls.__table__.columns}
        filtered = {k: v for k, v in data.items() if k in fields}
        return cls(**filtered)
