"""
Router para gestión de películas en el Sistema de Gestión de Cine.

Incluye operaciones CRUD para películas.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Movie, User
from schemas import MovieCreate, MovieResponse, MovieUpdate
from auth import get_current_empleado

router = APIRouter()


@router.post("/", response_model=MovieResponse)
async def create_movie(
    movie: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado),
):
    """
    Crear una nueva película. Empleados y gerentes pueden crear películas.
    """
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie)
    return db_movie


@router.get("/", response_model=List[MovieResponse])
async def read_movies(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de películas. Acceso público.
    """
    result = await db.execute(select(Movie).offset(skip).limit(limit))
    movies = result.scalars().all()
    return movies


@router.get("/{movie_id}", response_model=MovieResponse)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtener una película por ID. Acceso público.
    """
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalars().first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado),
):
    """
    Actualizar una película. Empleados y gerentes pueden actualizar.
    """
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalars().first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    for field, value in movie_update.dict(exclude_unset=True).items():
        setattr(movie, field, value)

    await db.commit()
    await db.refresh(movie)
    return movie


@router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_empleado),
):
    """
    Eliminar una película. Empleados y gerentes pueden eliminar.
    """
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalars().first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    await db.delete(movie)
    await db.commit()
    return {"message": "Movie deleted successfully"}
