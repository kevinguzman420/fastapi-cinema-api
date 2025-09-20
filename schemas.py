"""
Esquemas Pydantic para validación de datos en el Sistema de Gestión de Cine.

Define modelos para requests, responses y validaciones.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import UserRole, BookingStatus

# Esquemas para User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.cliente

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Esquemas para Movie
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int
    genre: Optional[str] = None
    release_date: Optional[datetime] = None

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[str] = None
    release_date: Optional[datetime] = None

class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Esquemas para Showtime
class ShowtimeBase(BaseModel):
    movie_id: int
    theater: str
    start_time: datetime
    end_time: datetime
    available_seats: int = 100
    price: int  # precio en centavos

class ShowtimeCreate(ShowtimeBase):
    pass

class ShowtimeUpdate(BaseModel):
    movie_id: Optional[int] = None
    theater: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    available_seats: Optional[int] = None
    price: Optional[int] = None

class ShowtimeResponse(ShowtimeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Esquemas para Booking
class BookingBase(BaseModel):
    user_id: int
    showtime_id: int
    seats_booked: int = 1

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None

class BookingResponse(BookingBase):
    id: int
    booking_time: datetime
    status: BookingStatus
    total_price: int

    class Config:
        from_attributes = True

# Esquemas para autenticación
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None