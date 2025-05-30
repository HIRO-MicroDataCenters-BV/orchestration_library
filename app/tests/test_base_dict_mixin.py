import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.models.base_dict_mixin import BaseDictMixin

Base = declarative_base()

class DummyModel(Base, BaseDictMixin):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

@pytest.fixture(scope="module")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_to_dict(session):
    obj = DummyModel(id=1, name="test")
    session.add(obj)
    session.commit()
    assert obj.to_dict() == {"id": 1, "name": "test"}

def test_from_dict():
    data = {"id": 2, "name": "example", "extra": "ignored"}
    obj = DummyModel.from_dict(data)
    assert isinstance(obj, DummyModel)
    assert obj.id == 2
    assert obj.name == "example"
    # 'extra' should not be set as an attribute
    assert not hasattr(obj, "extra")