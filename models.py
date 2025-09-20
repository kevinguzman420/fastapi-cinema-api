"""
Modelos de base de datos para el Sistema de Gestión de Cine.

Define las tablas principales: User, Movie, Showtime, Booking.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class UserRole(enum.Enum):
    """Enumeración para los roles de usuario."""
    cliente = "cliente"
    empleado = "empleado"
    gerente = "gerente"

class User(Base):
    """Modelo para usuarios del sistema."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.cliente)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    bookings = relationship("Booking", back_populates="user")

class Movie(Base):
    """Modelo para películas."""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    duration = Column(Integer, nullable=False)  # en minutos
    genre = Column(String(100))
    release_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    showtimes = relationship("Showtime", back_populates="movie")

class Showtime(Base):
    """Modelo para horarios de proyección."""
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    theater = Column(String(100), nullable=False)  # nombre del teatro
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    available_seats = Column(Integer, nullable=False, default=100)
    price = Column(Integer, nullable=False)  # precio en centavos o unidades
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    movie = relationship("Movie", back_populates="showtimes")
    bookings = relationship("Booking", back_populates="showtime")

class BookingStatus(enum.Enum):
    """Enumeración para el estado de las reservas."""
    confirmed = "confirmed"
    cancelled = "cancelled"
    pending = "pending"

class Booking(Base):
    """Modelo para reservas."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"), nullable=False)
    seats_booked = Column(Integer, nullable=False, default=1)
    booking_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.pending)
    total_price = Column(Integer, nullable=False)  # precio total en centavos

    # Relaciones
    user = relationship("User", back_populates="bookings")
    showtime = relationship("Showtime", back_populates="bookings")