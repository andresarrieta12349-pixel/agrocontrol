"""
auth.py
-------
Módulo de autenticación de AgroControl Pro.

- Hashing de contraseñas con bcrypt (passlib).
- Emisión y validación de JWT.
- Bootstrap del usuario maestro de pruebas:
      identificador: "julian arrieta"  (nombre de usuario / correo / teléfono)
      password:      "arrieta"
  Este usuario se crea automáticamente al iniciar la aplicación si no
  existe, y su contraseña siempre queda almacenada como hash bcrypt
  (nunca en texto plano) en la base de datos.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clave-de-desarrollo-agrocontrol-pro")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

MASTER_USER_NAME = os.getenv("MASTER_USER_NAME", "julian arrieta")
MASTER_USER_PASSWORD = os.getenv("MASTER_USER_PASSWORD", "arrieta")
MASTER_USER_EMAIL = os.getenv("MASTER_USER_EMAIL", "julian.arrieta@agrocontrolpro.com")
MASTER_USER_PHONE = os.getenv("MASTER_USER_PHONE", "3000000000")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


# ---------------------------------------------------------------------------
# Utilidades de hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Búsqueda de usuario por correo, teléfono o nombre de usuario
# ---------------------------------------------------------------------------
def obtener_usuario_por_identificador(db: Session, identificador: str) -> Optional[models.Usuario]:
    identificador_normalizado = identificador.strip().lower()
    return (
        db.query(models.Usuario)
        .filter(
            or_(
                models.Usuario.nombre_usuario.ilike(identificador_normalizado),
                models.Usuario.correo.ilike(identificador_normalizado),
                models.Usuario.telefono == identificador.strip(),
            )
        )
        .first()
    )


def autenticar_usuario(db: Session, identificador: str, password: str) -> Optional[models.Usuario]:
    usuario = obtener_usuario_por_identificador(db, identificador)
    if not usuario or not usuario.activo:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario


# ---------------------------------------------------------------------------
# Dependencia: usuario autenticado actual
# ---------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credenciales_invalidas

    payload = decode_access_token(token)
    usuario_id: Optional[str] = payload.get("sub")
    if usuario_id is None:
        raise credenciales_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None or not usuario.activo:
        raise credenciales_invalidas
    return usuario


def requerir_rol(*roles_permitidos: models.RolUsuario):
    """Fábrica de dependencias para restringir endpoints por rol."""

    def dependencia(usuario_actual: models.Usuario = Depends(get_current_user)):
        if usuario_actual.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes para esta operación",
            )
        return usuario_actual

    return dependencia


# ---------------------------------------------------------------------------
# Bootstrap del usuario maestro de pruebas (julian arrieta / arrieta)
# ---------------------------------------------------------------------------
def sembrar_usuario_maestro(db: Session) -> None:
    """
    Garantiza que el usuario maestro de pruebas exista siempre con
    credenciales válidas, encriptando la contraseña con bcrypt.
    Se ejecuta en el evento de arranque de la aplicación (ver main.py).
    """
    existente = obtener_usuario_por_identificador(db, MASTER_USER_NAME)
    if existente:
        # Asegura que la contraseña maestra siga siendo válida aunque
        # la BD ya tuviera el registro de una ejecución anterior.
        if not verify_password(MASTER_USER_PASSWORD, existente.password_hash):
            existente.password_hash = hash_password(MASTER_USER_PASSWORD)
            db.commit()
        return

    usuario_maestro = models.Usuario(
        nombre_completo="Julian Arrieta",
        nombre_usuario=MASTER_USER_NAME,
        correo=MASTER_USER_EMAIL,
        telefono=MASTER_USER_PHONE,
        password_hash=hash_password(MASTER_USER_PASSWORD),
        rol=models.RolUsuario.ADMIN,
        activo=True,
    )
    db.add(usuario_maestro)
    db.commit()
