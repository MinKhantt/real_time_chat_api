import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_async_session
# Ensure this import matches your actual dependency location
from app.core.auth import get_current_user 

# --- Database Setup ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# --- Mocks ---

@pytest.fixture
def mock_redis(mocker):
    """Mock the Redis client used in services."""
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    mocker.patch("app.services.user.redis_client", redis_mock)
    return redis_mock

@pytest.fixture
def mock_user_auth(test_user_data):
    """Return a user object to bypass authentication."""
    user = MagicMock()
    user.id = "test-user-id"
    user.email = test_user_data["email"]
    user.full_name = test_user_data["full_name"]
    return user

@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User",
    }

# --- Clients ---

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, mock_redis):
    """
    Base Unauthenticated Client.
    Use this for: /login, /register, and public endpoints.
    """
    # 1. Override Database
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides after test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def authorized_client(client: AsyncClient, mock_user_auth):
    """
    Authenticated Client.
    Use this for: protected endpoints (e.g., /users/me, CRUD).
    Overrides get_current_user to return a mock user.
    """
    def override_get_current_user():
        return mock_user_auth

    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield client
    
    # No specific teardown needed here as 'client' handles the clear(),
    # but strictly speaking, we can remove this specific key:
    # app.dependency_overrides.pop(get_current_user, None)