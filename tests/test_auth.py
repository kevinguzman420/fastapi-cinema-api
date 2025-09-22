"""
Tests para endpoints de autenticación.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_password_hash
from models import User


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session, unique_id):
    """
    Fixture que crea un usuario de test.
    """
    hashed_password = get_password_hash("testpass")
    user = User(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password_hash=hashed_password,
        role="cliente"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestAuth:
    """Tests para autenticación."""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """
        Test login exitoso con credenciales válidas.
        """
        response = client.post(
            "/auth/token",
            data={"username": test_user.username, "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """
        Test login fallido con contraseña incorrecta.
        """
        response = client.post(
            "/auth/token",
            data={"username": test_user.username, "password": "wrongpass"}
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_wrong_username(self, client):
        """
        Test login fallido con usuario inexistente.
        """
        response = client.post(
            "/auth/token",
            data={"username": "nonexistent", "password": "testpass"}
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """
        Test login con campos faltantes.
        """
        response = client.post(
            "/auth/token",
            data={"username": "testuser"}  # Sin password
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_root_endpoint(self, client):
        """
        Test endpoint raíz.
        """
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()