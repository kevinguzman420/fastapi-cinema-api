# Sistema de Gestión de Cine

API REST completa para gestión de cine con FastAPI, PostgreSQL y autenticación JWT.

## 🚀 Características

- **Autenticación JWT** con roles (Cliente, Empleado, Gerente)
- **Gestión completa** de películas, horarios y reservas
- **Base de datos PostgreSQL** con SQLAlchemy async
- **Validación automática** con Pydantic
- **Documentación interactiva** con Swagger UI
- **Operaciones CRUD** completas
- **Mejores prácticas** de desarrollo

## 📋 Requisitos

- Python 3.12+
- PostgreSQL 12+
- uv (gestor de paquetes)

## 🛠️ Instalación

### 1. Clonar e instalar dependencias

```bash
# Instalar dependencias
uv sync
```

### 2. Configurar PostgreSQL

**Opción A: Configuración automática (recomendado)**

```bash
# Ejecutar script de configuración
uv run python setup_db.py
```

**Opción B: Configuración manual**

```sql
-- Conectar como superusuario
CREATE USER cinema_user WITH PASSWORD 'cinema_pass';
CREATE DATABASE cinema_db OWNER cinema_user;
GRANT ALL PRIVILEGES ON DATABASE cinema_db TO cinema_user;
```

### 3. Crear tablas

**Opción A: Usando Alembic (recomendado para desarrollo)**
```bash
# Crear migraciones
uv run alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
uv run alembic upgrade head
```

**Opción B: Script alternativo (más confiable en CI/CD)**
```bash
# Crear tablas directamente
uv run python run_migrations.py
```

## 🚀 Uso

### Iniciar la aplicación

```bash
# Modo desarrollo
uv run uvicorn main:app --reload

# Modo producción
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Acceder a la aplicación

- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Docs alternativos**: http://localhost:8000/redoc

## 📚 Endpoints Principales

### Autenticación
- `POST /auth/token` - Login y obtener token JWT

### Usuarios (Solo Gerentes)
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

### Películas (Empleados/Gerentes)
- `GET /movies/` - Listar películas (público)
- `GET /movies/{id}` - Obtener película (público)
- `POST /movies/` - Crear película
- `PUT /movies/{id}` - Actualizar película
- `DELETE /movies/{id}` - Eliminar película

### Horarios (Empleados/Gerentes)
- `GET /showtimes/` - Listar horarios (público)
- `GET /showtimes/{id}` - Obtener horario (público)
- `POST /showtimes/` - Crear horario
- `PUT /showtimes/{id}` - Actualizar horario
- `DELETE /showtimes/{id}` - Eliminar horario

### Reservas
- `GET /bookings/` - Ver reservas del usuario
- `GET /bookings/{id}` - Obtener reserva
- `POST /bookings/` - Crear reserva (clientes)
- `PUT /bookings/{id}` - Actualizar reserva (empleados)
- `DELETE /bookings/{id}` - Cancelar reserva

## 🔐 Autenticación y Roles

### Roles del Sistema
- **Cliente**: Puede ver películas/horarios y gestionar sus reservas
- **Empleado**: Puede gestionar películas, horarios y reservas de todos
- **Gerente**: Acceso completo a todo el sistema

### Cómo usar la autenticación

```bash
# 1. Crear usuario gerente (sin autenticación)
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@cinema.com",
    "password": "admin123",
    "role": "gerente"
  }'

# 2. Hacer login
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 3. Usar token en requests
curl -X POST "http://localhost:8000/movies/" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Avatar 2",
    "description": "Secuela de Avatar",
    "duration": 180,
    "genre": "Ciencia Ficción"
  }'
```

## 🏗️ Arquitectura

```
cinema-management/
├── main.py              # Aplicación FastAPI principal
├── database.py          # Configuración de BD
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── auth.py              # Autenticación JWT
├── routers/             # Endpoints de la API
│   ├── auth_router.py
│   ├── users.py
│   ├── movies.py
│   ├── showtimes.py
│   └── bookings.py
├── alembic/             # Migraciones de BD
├── setup_db.py          # Script de configuración
└── pyproject.toml       # Dependencias
```

## 🧪 Pruebas

### Pruebas locales
```bash
# Ejecutar pruebas (si se implementan)
uv run pytest
```

### Pruebas de conexión a BD
```bash
# Probar conexión a PostgreSQL
uv run python test_db_connection.py
```

### CI/CD con Jenkins

El proyecto incluye configuración para Jenkins. Asegúrate de:

1. **Configurar PostgreSQL** en el servidor Jenkins
2. **Variables de entorno** correctas:
   ```bash
   DATABASE_URL=postgresql+asyncpg://cinema_user:cinema_pass@localhost:5432/cinema_db
   SECRET_KEY=your-secret-key-here
   ```

3. **Configurar BD** antes de ejecutar el pipeline:
   ```bash
   uv run python setup_db.py
   ```

#### Solución a errores de drivers y greenlets

##### Error 1: "asyncio extension requires async driver"
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
```

**Solución:** Usar `asyncpg` en lugar de `psycopg2`:
- ✅ `postgresql+asyncpg://...` (correcto para async)
- ❌ `postgresql+psycopg2://...` (síncrono, no funciona con async)

##### Error 2: "MissingGreenlet: greenlet_spawn has not been called"
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

**Solución:** Alembic modificado para manejar async correctamente. Si persiste, usa el script alternativo:
```bash
# Script alternativo para migraciones en CI/CD
uv run python run_migrations.py
```

## 📦 Despliegue

### Variables de entorno

Copia `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Variables principales:
```bash
# Base de datos (IMPORTANTE: usar asyncpg, no psycopg2)
DATABASE_URL=postgresql+asyncpg://cinema_user:cinema_pass@localhost:5432/cinema_db

# JWT
SECRET_KEY=your-secret-key-here-change-this-in-production

# Aplicación
APP_ENV=production
DEBUG=false
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --no-dev
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Soporte

Para soporte, abre un issue en el repositorio o contacta al equipo de desarrollo.