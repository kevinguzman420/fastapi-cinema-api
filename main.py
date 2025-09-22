"""
Aplicación principal del Sistema de Gestión de Cine.

Configura FastAPI con rutas, middlewares y base de datos.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, movies, showtimes, bookings, auth_router
from routers.showtimes import router as showtimes_router
from routers.bookings import router as bookings_router

# Crear las tablas en la base de datos (en desarrollo)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Cine",
    description="API para gestión de cine con autenticación y reservas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router.router, prefix="/auth", tags=["autenticación"])
app.include_router(users.router, prefix="/users", tags=["usuarios"])
app.include_router(movies.router, prefix="/movies", tags=["películas"])
app.include_router(showtimes_router, prefix="/showtimes", tags=["horarios"])
app.include_router(bookings_router, prefix="/bookings", tags=["reservas"])

@app.on_event("startup")
async def startup_event():
    """Evento de inicio: crear tablas."""
    await create_tables()

@app.get("/")
async def root():
    """Endpoint raíz."""
    return {"message": "Masha and Mincho"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
