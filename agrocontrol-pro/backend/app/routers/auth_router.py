"""
routers/auth_router.py
-----------------------
Endpoints de autenticación: /api/auth/register, /api/auth/login y /api/auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.auth import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UsuarioRegister, db: Session = Depends(get_db)):
    """Registra un usuario operativo usando correo y contraseña."""
    try:
        usuario = auth_service.register(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol.value})
    return schemas.TokenResponse(
        access_token=token,
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        usuario=usuario,
    )


@router.post("/login", response_model=schemas.TokenResponse, summary="Iniciar sesión")
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica al usuario usando **correo, teléfono o nombre de usuario**
    junto con su contraseña, y retorna un token JWT.

    Credenciales maestras de prueba:
    - identificador: `julian arrieta`
    - password: `arrieta`
    """
    usuario = auth_service.authenticate(db, payload.identificador, payload.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador o contraseña incorrectos",
        )

    token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol.value})
    return schemas.TokenResponse(
        access_token=token,
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        usuario=usuario,
    )


@router.post("/google", response_model=schemas.TokenResponse, summary="Iniciar sesión con Google")
def google_login(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Autentica o registra a un usuario mediante su cuenta de Google.
    """
    try:
        usuario = auth_service.authenticate_google(db, payload.correo, payload.nombre_completo)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol.value})
    return schemas.TokenResponse(
        access_token=token,
        expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        usuario=usuario,
    )


@router.get("/me", response_model=schemas.UsuarioOut, summary="Usuario autenticado actual")
def me(usuario_actual: models.Usuario = Depends(get_current_user)):
    return usuario_actual
