import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.user import User
from app.core.security import get_hashed_password

# NOTE: We use 'authorized_client' here to bypass auth checks automatically

@pytest.mark.asyncio
async def test_create_user(authorized_client: AsyncClient, test_user_data: dict):
    """Test creating a user via API."""
    response = await authorized_client.post(
        "/api/v1/users/",
        json=test_user_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_get_all_users(authorized_client: AsyncClient, db_session: AsyncSession):
    """Test getting all users."""
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            hashed_password=get_hashed_password("Test123!@#"),
            full_name=f"User {i}",
        )
        db_session.add(user)
    await db_session.commit()
    
    response = await authorized_client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_single_user(authorized_client: AsyncClient, db_session: AsyncSession):
    """Test getting a single user by ID."""
    user = User(
        email="single@example.com",
        hashed_password=get_hashed_password("Test123!@#"),
        full_name="Single User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    response = await authorized_client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["email"] == "single@example.com"


@pytest.mark.asyncio
async def test_get_user_not_found(authorized_client: AsyncClient):
    """Test getting a user that doesn't exist."""
    fake_id = uuid4()
    response = await authorized_client.get(f"/api/v1/users/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(
    authorized_client: AsyncClient, db_session: AsyncSession, test_user_data: dict
):
    """Test updating a user."""
    user = User(
        email=test_user_data["email"],
        hashed_password=get_hashed_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    update_data = {"full_name": "Updated Name"}
    response = await authorized_client.put(
        f"/api/v1/users/{user.id}",
        json=update_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_user(
    authorized_client: AsyncClient, db_session: AsyncSession, test_user_data: dict
):
    """Test deleting a user."""
    user = User(
        email=test_user_data["email"],
        hashed_password=get_hashed_password(test_user_data["password"]),
        full_name=test_user_data["full_name"],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    response = await authorized_client.delete(f"/api/v1/users/{user.id}")
    assert response.status_code == 204
    
    get_response = await authorized_client.get(f"/api/v1/users/{user.id}")
    assert get_response.status_code == 404