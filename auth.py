"""
Módulo de autenticación para el Sistema de Gestión de Cine.

Incluye funciones para hashing de contraseñas, creación de tokens JWT y verificación.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User
from schemas import TokenData

# Configuración de seguridad
SECRET_KEY = "your-secret-key-here"  # En producción, usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)  # Token con 1 día de vida
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(db: AsyncSession, username: str) -> Optional[User]:
    """Obtiene un usuario por nombre de usuario."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Autentica a un usuario con nombre de usuario y contraseña."""
    user = await get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Obtiene el usuario actual desde el token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("--- FLAG ---")
        print("--- FLAG ---")
        print("--- FLAG ---")
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtiene el usuario actual activo."""
    return current_user

# Dependencias para roles
async def get_current_cliente(current_user: User = Depends(get_current_user)) -> User:
    """Verifica que el usuario sea cliente."""
    if current_user.role != "cliente":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_current_empleado(current_user: User = Depends(get_current_user)) -> User:
    """Verifica que el usuario sea empleado."""
    if current_user.role == "empleado":
        raise HTTPException(status_code=403, detail="Not enough permissionss")
    return current_user

async def get_current_gerente(current_user: User = Depends(get_current_user)) -> User:
    """Verifica que el usuario sea gerente."""
    if current_user.role != "gerente":
        raise HTTPException(status_code=403, detail="Not enough permissionsss")
    return current_user

async def get_current_gerente_optional(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """Obtiene el gerente actual si está autenticado, None si no."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = await get_user(db, username=username)
        if user and user.role == "gerente":
            return user
        return None
    except JWTError:
        return None