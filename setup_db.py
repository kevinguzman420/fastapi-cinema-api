#!/usr/bin/env python3
"""
Script para configurar la base de datos PostgreSQL para el Sistema de Gestión de Cine.

Este script crea la base de datos, usuario y tablas necesarias.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base


async def setup_database():
    """Configura la base de datos PostgreSQL."""

    # Conectar como superusuario para crear BD y usuario
    admin_url = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

    print("🔧 Configurando base de datos PostgreSQL...")

    try:
        # Crear motor de conexión como admin
        admin_engine = create_async_engine(admin_url, echo=True)

        async with admin_engine.begin() as conn:
            # Crear usuario si no existe
            print("👤 Creando usuario 'cinema_user'...")
            await conn.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cinema_user') THEN
                        CREATE ROLE cinema_user LOGIN PASSWORD 'cinema_pass';
                    END IF;
                END
                $$;
            """
            )

            # Crear base de datos si no existe
            print("📊 Creando base de datos 'cinema_db'...")
            await conn.execute(
                """
                SELECT 'CREATE DATABASE cinema_db OWNER cinema_user'
                WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cinema_db')
            """
            )

            # Otorgar permisos
            print("🔑 Otorgando permisos...")
            await conn.execute(
                "GRANT ALL PRIVILEGES ON DATABASE cinema_db TO cinema_user;"
            )

        await admin_engine.dispose()
        print("✅ Usuario y base de datos creados exitosamente!")

        # Ahora crear tablas con el usuario de la aplicación
        # app_url = "postgresql+asyncpg://kevinguzman:kevinguzman@localhost:5432/cinema_db"
        # app_url = (
        #     "postgresql+asyncpg://kevinguzman:kevinguzman@localhost:5432/cinema_db"
        # )
        app_url = (
            "postgresql+psycopg2://cinema_user:cinema_pass@localhost:5432/cinema_db"
        )

        app_engine = create_async_engine(app_url, echo=True)

        async with app_engine.begin() as conn:
            print("📋 Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)

        await app_engine.dispose()
        print("✅ Tablas creadas exitosamente!")

        print("\n🎉 Base de datos configurada correctamente!")
        print("📝 Credenciales:")
        print("   Usuario: cinema_user")
        print("   Contraseña: cinema_pass")
        print("   Base de datos: cinema_db")
        print("   Puerto: 5432")

    except Exception as e:
        print(f"❌ Error configurando la base de datos: {e}")
        print("\n🔧 Asegúrate de que:")
        print("   1. PostgreSQL esté instalado y ejecutándose")
        print("   2. El usuario 'postgres' tenga contraseña 'password'")
        print("   3. PostgreSQL esté escuchando en localhost:5432")
        return False

    return True


if __name__ == "__main__":
    asyncio.run(setup_database())
