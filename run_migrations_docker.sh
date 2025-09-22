#!/bin/bash

# Script para ejecutar migraciones de base de datos en el contenedor Docker

echo "🚀 Ejecutando migraciones en Docker..."

# Ejecutar el script de migraciones dentro del contenedor de la app
docker-compose exec app uv run python run_migrations.py

if [ $? -eq 0 ]; then
    echo "✅ Migraciones completadas exitosamente!"
else
    echo "❌ Error al ejecutar migraciones."
    exit 1
fi