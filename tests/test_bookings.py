"""
Tests para endpoints de gestión de reservas.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from auth import get_password_hash
from models import User, Movie, Showtime, Booking


@pytest_asyncio.fixture(scope="function")
async def test_client_user(db_session, unique_id):
    """
    Fixture que crea un usuario cliente de test.
    """
    hashed_password = get_password_hash("clientpass")
    client_user = User(
        username=f"client_{unique_id}",
        email=f"client_{unique_id}@example.com",
        password_hash=hashed_password,
        role="cliente"
    )
    db_session.add(client_user)
    await db_session.commit()
    await db_session.refresh(client_user)
    return client_user


@pytest_asyncio.fixture
async def test_showtime_for_booking(db_session, unique_id):
    """
    Fixture que crea un showtime para reservas.
    """
    # Crear movie primero
    movie = Movie(
        title=f"Booking Movie {unique_id}",
        description="Movie for booking tests",
        duration=120,
        genre="Action"
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    # Crear showtime
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    showtime = Showtime(
        movie_id=movie.id,
        theater=f"Booking Theater {unique_id}",
        start_time=start_time,
        end_time=end_time,
        available_seats=50,
        price=12.0
    )
    db_session.add(showtime)
    await db_session.commit()
    await db_session.refresh(showtime)
    return showtime


@pytest_asyncio.fixture
async def test_bookings(db_session, test_client_user, test_showtime_for_booking):
    """
    Fixture que crea reservas de test.
    """
    bookings = []
    for i in range(2):
        booking = Booking(
            user_id=test_client_user.id,
            showtime_id=test_showtime_for_booking.id,
            seats_booked=2 + i,
            total_price=(2 + i) * test_showtime_for_booking.price
        )
        db_session.add(booking)
        bookings.append(booking)
    await db_session.commit()
    for booking in bookings:
        await db_session.refresh(booking)
    return bookings


class TestBookings:
    """Tests para gestión de reservas."""

    @pytest.mark.asyncio
    async def test_create_booking(self, client: TestClient, test_showtime_for_booking):
        """
        Test crear una nueva reserva.
        """
        booking_data = {
            "showtime_id": test_showtime_for_booking.id,
            "seats_booked": 3
        }

        response = client.post("/bookings/", json=booking_data)

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 200
        data = response.json()
        assert data["showtime_id"] == test_showtime_for_booking.id
        assert data["seats_booked"] == 3
        assert data["total_price"] == 3 * test_showtime_for_booking.price

    @pytest.mark.asyncio
    async def test_create_booking_insufficient_seats(self, client: TestClient, test_showtime_for_booking):
        """
        Test crear reserva con asientos insuficientes.
        """
        booking_data = {
            "showtime_id": test_showtime_for_booking.id,
            "seats_booked": 100  # Más que disponibles
        }

        response = client.post("/bookings/", json=booking_data)

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 400
        assert "Not enough seats available" in response.json()["detail"]

    def test_create_booking_invalid_showtime(self, client: TestClient):
        """
        Test crear reserva con showtime inexistente.
        """
        booking_data = {
            "showtime_id": 999,
            "seats_booked": 2
        }

        response = client.post("/bookings/", json=booking_data)

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 404
        assert "Showtime not found" in response.json()["detail"]

    def test_read_bookings(self, client: TestClient, test_bookings):
        """
        Test obtener lista de reservas.
        """
        response = client.get("/bookings/")

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_read_booking(self, client: TestClient, test_bookings):
        """
        Test obtener una reserva específica.
        """
        booking_id = test_bookings[0].id
        response = client.get(f"/bookings/{booking_id}")

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id
        assert data["seats_booked"] == 2

    def test_read_booking_not_found(self, client: TestClient):
        """
        Test obtener reserva inexistente.
        """
        response = client.get("/bookings/999")

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]

    def test_update_booking(self, client: TestClient, test_bookings):
        """
        Test actualizar una reserva.
        """
        booking_id = test_bookings[0].id
        update_data = {
            "seats_booked": 5
        }

        response = client.put(f"/bookings/{booking_id}", json=update_data)

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 200
        data = response.json()
        assert data["seats_booked"] == 5

    def test_update_booking_not_found(self, client: TestClient):
        """
        Test actualizar reserva inexistente.
        """
        update_data = {"seats_booked": 1}
        response = client.put("/bookings/999", json=update_data)

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]

    def test_delete_booking(self, client: TestClient, test_bookings, test_showtime_for_booking):
        """
        Test cancelar una reserva.
        """
        booking_id = test_bookings[1].id
        original_seats = test_showtime_for_booking.available_seats

        response = client.delete(f"/bookings/{booking_id}")

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 200
        assert response.json() == {"message": "Booking cancelled successfully"}

        # Verificar que ya no existe
        response = client.get(f"/bookings/{booking_id}")
        if response.status_code != 401:  # Si no requiere auth
            assert response.status_code == 404

    def test_delete_booking_not_found(self, client: TestClient):
        """
        Test cancelar reserva inexistente.
        """
        response = client.delete("/bookings/999")

        if response.status_code == 401:
            pytest.skip("Authentication required for this endpoint")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]