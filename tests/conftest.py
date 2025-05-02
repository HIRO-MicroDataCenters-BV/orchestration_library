import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.routes import workload_request
from app.database import get_async_db


@pytest.fixture()
async def client(db_session):
    app = FastAPI()
    app.include_router(workload_request.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
