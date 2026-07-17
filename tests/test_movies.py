import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_movies():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First login to get token
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "movieuser",
                "email": "movie@example.com",
                "password": "testpass123"
            }
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "movie@example.com",
                "password": "testpass123"
            }
        )
        token = login.json()["token"]
        
        response = await client.get(
            "/api/v1/movies/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_trending_movies():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/movies/trending")
        assert response.status_code == 200
        assert isinstance(response.json(), list)