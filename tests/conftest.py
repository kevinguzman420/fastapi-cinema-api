"""
Configuración de fixtures para tests con pytest.

Proporciona fixtures para la aplicación FastAPI, cliente HTTP y base de datos de test.
"""

import asyncio
from typing import AsyncGenerator
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# Crear motor de BD en memoria para tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

test_async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Override para get_db que usa la BD de test.
    """
    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="session")
def event_loop():
    """
    Crear un event loop para tests asíncronos.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """
    Fixture que proporciona la aplicación FastAPI configurada para tests.
    """
    # Override la dependencia de BD
    app.dependency_overrides[get_db] = override_get_db

    # Crear tablas en la BD de test
    import asyncio
    asyncio.run(create_tables())

    yield app

    # Limpiar después de los tests
    asyncio.run(drop_tables())


async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def client(test_app: FastAPI):
    """
    Fixture que proporciona un cliente HTTP para tests.
    """
    # Usar TestClient que es sync pero funciona con FastAPI async
    client = TestClient(test_app)
    yield client


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture que proporciona una sesión de BD limpia para cada test.
    """
    import asyncio
    session = asyncio.run(get_session())
    try:
        yield session
    finally:
        # Limpiar la sesión después de cada test
        asyncio.run(cleanup_session(session))


async def get_session():
    return test_async_session()


async def cleanup_session(session):
    try:
        await session.rollback()
        await session.close()
    except:
        pass


@pytest.fixture(scope="function")
def unique_id():
    """
    Fixture que proporciona un ID único para cada test.
    """
    return str(uuid.uuid4())[:8]