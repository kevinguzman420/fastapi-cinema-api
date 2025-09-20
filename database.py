"""
Configuración de la base de datos para el Sistema de Gestión de Cine.

Este módulo configura la conexión asíncrona a PostgreSQL usando SQLAlchemy.
"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# URL de la base de datos, por defecto usa variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://kevinguzman:kevinguzman@localhost:5432/cinema_db"  # PostgreSQL para desarrollo
)

# Crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear la fábrica de sesiones asíncronas
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base declarativa para los modelos
class Base(DeclarativeBase):
    pass

# Función para obtener una sesión de base de datos
async def get_db():
    """
    Generador asíncrono que proporciona una sesión de base de datos.

    Yields:
        AsyncSession: Sesión de base de datos para operaciones CRUD.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()