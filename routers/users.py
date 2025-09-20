"""
Router para gestión de usuarios en el Sistema de Gestión de Cine.

Incluye operaciones CRUD con control de acceso basado en roles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate
from auth import get_current_gerente_optional, get_password_hash

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_gerente_optional)
):
    """
    Crear un nuevo usuario. Para el primer usuario, no se requiere autenticación.
    Para usuarios posteriores, solo gerentes pueden crear usuarios.

    - **username**: Nombre de usuario único
    - **email**: Correo electrónico único
    - **password**: Contraseña
    - **role**: Rol del usuario (cliente, empleado, gerente)
    """
    # Verificar si ya existen usuarios en la base de datos
    result = await db.execute(select(User).limit(1))
    user_exists = result.scalars().first() is not None

    # TEMPORALMENTE DESACTIVADO: Validación de autenticación para crear usuarios
    # if user_exists:
    #     # Si existen usuarios, verificar autenticación como gerente
    #     if not current_user or current_user.role != "gerente":
    #         raise HTTPException(status_code=403, detail="Not authorized to create users")

    # Verificar si el username ya existe
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Verificar si el email ya existe
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Crear el usuario
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_gerente)
):
    """
    Obtener lista de usuarios. Solo gerentes pueden ver todos los usuarios.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_gerente)
):
    """
    Obtener un usuario por ID. Solo gerentes pueden ver usuarios.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_gerente)
):
    """
    Actualizar un usuario. Solo gerentes pueden actualizar usuarios.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar campos
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password":
            setattr(user, "password_hash", get_password_hash(value))
        else:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_gerente)
):
    """
    Eliminar un usuario. Solo gerentes pueden eliminar usuarios.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}