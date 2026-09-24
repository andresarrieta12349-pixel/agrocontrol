"""
auth.py
-------
Módulo de autenticación de AgroControl Pro.

- Hashing de contraseñas con bcrypt (passlib).
- Emisión y validación de JWT.

No existe ningún usuario "maestro" ni cuenta creada automáticamente:
todo usuario debe registrarse con correo/contraseña o autenticarse con
Google (ver app/routers/auth_router.py y app/services/auth_service.py).

Seguridad del secreto JWT: quien conozca JWT_SECRET_KEY puede fabricar un
token de administrador. Por eso NO existe un valor por defecto:
- En producción, si falta o es débil (< 32 caracteres), la app NO arranca.
- En desarrollo se genera un secreto aleatorio temporal (las sesiones se
  cierran al reiniciar) y se muestra una advertencia.
"""
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.security import ES_PRODUCCION

logger = logging.getLogger("agrocontrol.auth")

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
_SECRETOS_CONOCIDOS = {
    "clave-de-desarrollo-agrocontrol-pro",
    "changeme",
    "cambiar-esta-clave",
    "secret",
}


def _cargar_secreto_jwt() -> str:
    secreto = os.getenv("JWT_SECRET_KEY", "").strip()
    es_debil = (not secreto) or secreto.lower() in _SECRETOS_CONOCIDOS or len(secreto) < 32
    if not es_debil:
        return secreto
    if ES_PRODUCCION:
        raise RuntimeError(
            "JWT_SECRET_KEY falta o es débil. Genera una con: "
            "python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    logger.warning(
        "JWT_SECRET_KEY no definida o débil: se usa una clave aleatoria temporal "
        "(las sesiones se cerrarán al reiniciar). Define una clave fuerte en .env."
    )
    return secrets.token_urlsafe(64)


JWT_SECRET_KEY = _cargar_secreto_jwt()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256").strip()
if JWT_ALGORITHM not in {"HS256", "HS384", "HS512"}:
    raise RuntimeError("JWT_ALGORITHM debe ser HS256, HS384 o HS512.")
# Vida corta = menos daño si un token se filtra (antes: 480 min = 8 horas).
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# Hash de mentira: se verifica cuando el usuario no existe, para que el login
# tarde lo mismo exista o no la cuenta (evita descubrir correos registrados).
_HASH_FALSO = pwd_context.hash(secrets.token_urlsafe(16))


# ---------------------------------------------------------------------------
# Utilidades de hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(plain_password, password_hash)
    except (ValueError, TypeError):
        # Contraseña demasiado larga para bcrypt o hash corrupto: se rechaza.
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    ahora = datetime.now(timezone.utc)
    to_encode.update({"exp": ahora + timedelta(minutes=expires_minutes), "iat": ahora})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require_exp": True},
        )
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
    # Comparación exacta (sin ILIKE): con ILIKE los caracteres "%" y "_" del
    # texto ingresado actuarían como comodines y podrían coincidir con otras cuentas.
    identificador_normalizado = identificador.strip().lower()
    return (
        db.query(models.Usuario)
        .filter(
            or_(
                func.lower(models.Usuario.nombre_usuario) == identificador_normalizado,
                func.lower(models.Usuario.correo) == identificador_normalizado,
                models.Usuario.telefono == identificador.strip(),
            )
        )
        .first()
    )


def autenticar_usuario(db: Session, identificador: str, password: str) -> Optional[models.Usuario]:
    usuario = obtener_usuario_por_identificador(db, identificador)
    # Siempre se hace una verificación bcrypt (real o falsa) para igualar tiempos.
    hash_a_verificar = usuario.password_hash if (usuario and usuario.password_hash) else _HASH_FALSO
    password_ok = verify_password(password or "", hash_a_verificar)

    if not usuario or not usuario.activo:
        return None
    # Las cuentas creadas por Google no tienen password_hash: no se les asigna
    # ninguna contraseña predeterminada, así que el login por contraseña
    # siempre debe rechazarse para ellas.
    if not usuario.password_hash or not password_ok:
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
    try:
        usuario_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credenciales_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
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
