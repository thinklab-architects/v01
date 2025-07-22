import os
import asyncio
import pytest
from typing import Generator, AsyncGenerator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import Base

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise SystemExit("FATAL: TEST_DATABASE_URL is not set in the .env file for testing.")

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# --- Fixture Scopes ---
# `session` scope: The fixture is created once per test session.
# `function` scope: The fixture is created for each test function.

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

import pytest_asyncio

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Create database tables before tests run and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test function."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback() # Rollback any changes to keep tests isolated

@pytest.fixture(scope="function")
def client(db_session: AsyncSession):
    """Provide an HTTP client with the database dependency overridden."""
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]