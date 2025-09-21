#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos.
"""

import asyncio
from database import engine, get_db
from models import Base

async def test_connection():
    """Prueba la conexión a la base de datos."""
    try:
        print("🔧 Probando conexión a la base de datos...")

        # Probar conexión básica
        async with engine.begin() as conn:
            print("✅ Conexión exitosa!")

            # Crear tablas si no existen
            print("📋 Creando tablas...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas!")

        # Probar sesión
        async for session in get_db():
            print("✅ Sesión de base de datos funcionando!")
            break

        print("🎉 ¡Todo funciona correctamente!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Posibles soluciones:")
        print("1. Asegúrate de que PostgreSQL esté ejecutándose")
        print("2. Verifica las credenciales en database.py")
        print("3. Ejecuta: python setup_db.py")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_connection())