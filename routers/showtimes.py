"""
Router para gestión de horarios de proyección en el Sistema de Gestión de Cine.

Incluye operaciones CRUD para horarios.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Showtime, User
from schemas import ShowtimeCreate, ShowtimeResponse, ShowtimeUpdate
from auth import get_current_empleado

router = APIRouter()

@router.post("/", response_model=ShowtimeResponse)
async def create_showtime(
    showtime: ShowtimeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado)
):
    """
    Crear un nuevo horario de proyección. Empleados y gerentes pueden crear.
    """
    # Verificar que la película existe
    from models import Movie
    result = await db.execute(select(Movie).where(Movie.id == showtime.movie_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Movie not found")

    db_showtime = Showtime(**showtime.dict())
    db.add(db_showtime)
    await db.commit()
    await db.refresh(db_showtime)
    return db_showtime

@router.get("/", response_model=List[ShowtimeResponse])
async def read_showtimes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de horarios de proyección. Acceso público.
    """
    result = await db.execute(select(Showtime).offset(skip).limit(limit))
    showtimes = result.scalars().all()
    return showtimes

@router.get("/{showtime_id}", response_model=ShowtimeResponse)
async def read_showtime(
    showtime_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un horario por ID. Acceso público.
    """
    result = await db.execute(select(Showtime).where(Showtime.id == showtime_id))
    showtime = result.scalars().first()
    if showtime is None:
        raise HTTPException(status_code=404, detail="Showtime not found")
    return showtime

@router.put("/{showtime_id}", response_model=ShowtimeResponse)
async def update_showtime(
    showtime_id: int,
    showtime_update: ShowtimeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado)
):
    """
    Actualizar un horario. Empleados y gerentes pueden actualizar.
    """
    result = await db.execute(select(Showtime).where(Showtime.id == showtime_id))
    showtime = result.scalars().first()
    if showtime is None:
        raise HTTPException(status_code=404, detail="Showtime not found")

    for field, value in showtime_update.dict(exclude_unset=True).items():
        setattr(showtime, field, value)

    await db.commit()
    await db.refresh(showtime)
    return showtime

@router.delete("/{showtime_id}")
async def delete_showtime(
    showtime_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado)
):
    """
    Eliminar un horario. Empleados y gerentes pueden eliminar.
    """
    result = await db.execute(select(Showtime).where(Showtime.id == showtime_id))
    showtime = result.scalars().first()
    if showtime is None:
        raise HTTPException(status_code=404, detail="Showtime not found")

    await db.delete(showtime)
    await db.commit()
    return {"message": "Showtime deleted successfully"}