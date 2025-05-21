"""
Tests for db setup and teardown using SQLAlchemy with FastAPI.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base  # Replace with your actual model import

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Use in-memory SQLite for testing

# Create an asynchronous engine for testing
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a sessionmaker
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Create a new database session for each test
@pytest.fixture(scope="function")
async def db_session():
    """
    Fixture to create a new database session for each test.
    """
    async with TestingSessionLocal() as session:
        # Create all tables for testing (if not already created)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield session

        # Cleanup: drop the tables after the test is done
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
