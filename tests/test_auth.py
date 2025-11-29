import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_hashed_password

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user_data: dict):
    """Test user registration endpoint."""
    response = await client.post(
        "/api/v1/auth/register",
        json=test_user_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "access_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user_data: dict):
    """Test registering with duplicate email."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    
    response = await client.post(
        "/api/v1/auth/register",
        json=test_user_data,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient, test_user_data: dict):
    """Test registering with weak password."""
    weak_password_data = test_user_data.copy()
    weak_password_data["password"] = "weak"
    
    response = await client.post(
        "/api/v1/auth/register",
        json=weak_password_data,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession, test_user_data: dict):
    """Test successful login."""
    hashed_password = get_hashed_password(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_incorrect_credentials(client: AsyncClient, db_session: AsyncSession, test_user_data: dict):
    hashed_password = get_hashed_password(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db_session: AsyncSession, test_user_data: dict):
    """Test token refresh endpoint."""
    hashed_password = get_hashed_password(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    data = login_response.json()
    
    # We try to get refresh_token, fallback to access_token if your app uses one for both
    refresh_token = data.get("refresh_token", data["access_token"])
    
    await asyncio.sleep(1.1) 
    
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    new_data = response.json()
    assert new_data["access_token"] != data["access_token"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db_session: AsyncSession, test_user_data: dict):
    """
    Test authenticating with a REAL token (integration test).
    Uses 'client' so no mock auth is injected.
    """
    hashed_password = get_hashed_password(test_user_data["password"])
    user = User(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": test_user_data["email"], "password": test_user_data["password"]},
    )
    token = login_response.json()["access_token"]
    
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401