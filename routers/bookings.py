"""
Router para gestión de reservas en el Sistema de Gestión de Cine.

Incluye operaciones CRUD para reservas con lógica de negocio.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Booking, User, Showtime
from schemas import BookingCreate, BookingResponse, BookingUpdate
from auth import get_current_cliente, get_current_empleado

router = APIRouter()

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_cliente)
):
    """
    Crear una nueva reserva. Solo clientes pueden reservar.
    """
    # Verificar que el showtime existe
    result = await db.execute(select(Showtime).where(Showtime.id == booking.showtime_id))
    showtime = result.scalars().first()
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")

    # Verificar asientos disponibles
    if showtime.available_seats < booking.seats_booked:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    # Calcular precio total
    total_price = showtime.price * booking.seats_booked

    # Crear reserva
    db_booking = Booking(
        user_id=current_user.id,
        showtime_id=booking.showtime_id,
        seats_booked=booking.seats_booked,
        total_price=total_price
    )
    db.add(db_booking)

    # Actualizar asientos disponibles
    showtime.available_seats -= booking.seats_booked

    await db.commit()
    await db.refresh(db_booking)
    return db_booking

@router.get("/", response_model=List[BookingResponse])
async def read_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_cliente)
):
    """
    Obtener reservas del usuario actual. Clientes ven sus reservas, empleados/gerentes ven todas.
    """
    if current_user.role == "cliente":
        result = await db.execute(select(Booking).where(Booking.user_id == current_user.id))
    else:
        result = await db.execute(select(Booking))
    bookings = result.scalars().all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
async def read_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_cliente)
):
    """
    Obtener una reserva por ID. Clientes solo ven sus reservas.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role == "cliente" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado)
):
    """
    Actualizar una reserva. Empleados y gerentes pueden actualizar.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    for field, value in booking_update.dict(exclude_unset=True).items():
        setattr(booking, field, value)

    await db.commit()
    await db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_cliente)
):
    """
    Cancelar una reserva. Clientes pueden cancelar sus reservas, empleados/gerentes cualquier.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if current_user.role == "cliente" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    # Devolver asientos
    result_showtime = await db.execute(select(Showtime).where(Showtime.id == booking.showtime_id))
    showtime = result_showtime.scalars().first()
    if showtime:
        showtime.available_seats += booking.seats_booked

    await db.delete(booking)
    await db.commit()
    return {"message": "Booking cancelled successfully"}