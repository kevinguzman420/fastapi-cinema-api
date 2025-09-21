#!/usr/bin/env python3
"""
Script alternativo para ejecutar migraciones de base de datos.
Más confiable que Alembic en entornos CI/CD con async.
"""

import asyncio
import os
from database import engine, Base

async def run_migrations():
    """Ejecuta las migraciones creando las tablas directamente."""
    try:
        print("🔧 Ejecutando migraciones de base de datos...")

        # Crear todas las tablas
        async with engine.begin() as conn:
            print("📋 Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas exitosamente!")

        print("🎉 Migraciones completadas!")

    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(run_migrations())
    exit(0 if success else 1)