"""
# app/models/base_dict_mixin.py
Test cases for BaseDictMixin
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from app.models.base_dict_mixin import BaseDictMixin

Base = declarative_base()

class DummyModel(Base, BaseDictMixin):
    """
    A dummy model for testing BaseDictMixin.
    This model is used to test the functionality of the BaseDictMixin methods.
    """
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

def test_to_dict():
    """
    Test the to_dict method of BaseDictMixin.
    This test checks if the model instance can be converted to a dictionary correctly.
    """

    obj = DummyModel(id=1, name="test")
    # No need to add/commit for to_dict test
    assert obj.to_dict() == {"id": 1, "name": "test"}

def test_from_dict():
    """
    Test the from_dict method of BaseDictMixin.
    This test checks if a model instance can be created from a dictionary.
    """
    data = {"id": 2, "name": "example", "extra": "ignored"}
    obj = DummyModel.from_dict(data)
    assert isinstance(obj, DummyModel)
    assert obj.id == 2
    assert obj.name == "example"
    # 'extra' should not be set as an attribute
    assert not hasattr(obj, "extra")
