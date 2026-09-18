"""
routers/auth_router.py
-----------------------
Endpoints de autenticación:
- POST /api/auth/register        -> registro local con correo/contraseña
- POST /api/auth/login           -> login local con correo/contraseña
- GET  /api/auth/google/login    -> redirige a Google (selector de cuentas)
- GET  /api/auth/google/callback -> Google regresa aquí con ?code=...&state=...
- GET  /api/auth/me              -> usuario autenticado actual

Login con Google (OAuth 2.0, flujo de redirección con código de autorización):
  1. El navegador navega a GET /api/auth/google/login.
  2. Este endpoint redirige (302) a la pantalla de Google, forzando el
     selector de cuentas (prompt=select_account) y fija una cookie de
     "state" firmada aleatoriamente (protección CSRF).
  3. El usuario elige su cuenta de Google en la propia página de Google.
  4. Google redirige el navegador a GOOGLE_REDIRECT_URI
     (GET /api/auth/google/callback?code=...&state=...).
  5. El backend valida el "state" contra la cookie, intercambia el "code"
     por tokens directamente con Google (usando GOOGLE_CLIENT_SECRET) y
     verifica el id_token recibido.
  6. Se busca o crea el usuario en la base de datos (nunca con contraseña
     predeterminada, ni con rol admin por defecto: ver auth_service.py).
  7. Se genera un JWT propio de AgroControl Pro y se redirige al usuario
     de vuelta al frontend, con el token en el fragmento de la URL
     (después de "#"), que nunca se envía a ningún servidor.
"""
import os
import secrets
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from google_auth_oauthlib.flow import Flow

from app import schemas, models
from app.database import get_db
from app.auth import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.services.auth_service import auth_service

# ---------------------------------------------------------------------------
# Configuración de Google OAuth 2.0 (flujo de redirección con código)
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "").strip()

# URL del frontend a donde se redirige al usuario ya autenticado.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080").strip().rstrip("/")

# En producción (HTTPS) esta variable debe ser "true" para que la cookie
# de "state" sólo viaje por conexiones seguras.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").strip().lower() == "true"

OAUTH_STATE_COOKIE = "agrocontrol_oauth_state"

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


def _construir_flow_google() -> Flow:
    """Crea el objeto Flow de google-auth-oauthlib con la configuración del servidor."""
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URI):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "La autenticación con Google no está configurada en el servidor "
                "(faltan GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET o GOOGLE_REDIRECT_URI)."
            ),
        )
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=["openid", "email", "profile"],
        redirect_uri=GOOGLE_REDIRECT_URI,
    )


def _redirigir_con_error(mensaje: str) -> RedirectResponse:
    """Devuelve al usuario al frontend con un mensaje de error legible."""
    destino = f"{FRONTEND_URL}/?auth_error={quote(mensaje)}"
    respuesta = RedirectResponse(url=destino, status_code=status.HTTP_302_FOUND)
    respuesta.delete_cookie(OAUTH_STATE_COOKIE)
    return respuesta


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

    Las cuentas creadas mediante Google no tienen contraseña y por lo
    tanto no pueden iniciar sesión por esta vía.
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


@router.get("/google/login", summary="Inicia el login con Google (redirige a Google)")
def google_login():
    """
    Redirige al navegador a la pantalla de selección de cuentas de Google.
    El parámetro prompt=select_account obliga a Google a mostrar siempre
    el selector, incluso si ya hay una sesión de Google activa.
    """
    flow = _construir_flow_google()
    estado = secrets.token_urlsafe(32)

    url_autorizacion, _ = flow.authorization_url(
        access_type="online",
        include_granted_scopes="true",
        prompt="select_account",
        state=estado,
    )

    respuesta = RedirectResponse(url=url_autorizacion, status_code=status.HTTP_302_FOUND)
    respuesta.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=estado,
        max_age=300,  # 5 minutos: tiempo de sobra para completar el login
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
    )
    return respuesta


@router.get("/google/callback", summary="Callback de Google OAuth 2.0")
def google_callback(
    request: Request,
    db: Session = Depends(get_db),
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Google redirige aquí después de que el usuario elige su cuenta.
    Valida el "state" (anti-CSRF), intercambia el código por tokens con
    Google, verifica el id_token y finalmente redirige al frontend con
    el JWT propio de la aplicación en el fragmento de la URL.
    """
    if error:
        # El usuario canceló el selector de cuentas o Google reportó un error.
        return _redirigir_con_error("El inicio de sesión con Google fue cancelado.")

    estado_cookie = request.cookies.get(OAUTH_STATE_COOKIE)
    if not code or not state or not estado_cookie or not secrets.compare_digest(state, estado_cookie):
        return _redirigir_con_error(
            "La solicitud de autenticación con Google no es válida o expiró. Intenta de nuevo."
        )

    flow = _construir_flow_google()
    try:
        token_google = flow.fetch_token(code=code)
    except Exception as e:
        # NOTA TEMPORAL DE DIAGNÓSTICO: imprime el error real en los logs
        # del backend (docker logs agrocontrol_backend) para poder ver
        # exactamente por qué Google rechazó el intercambio del código.
        print("ERROR GOOGLE TOKEN:", repr(e))
        return _redirigir_con_error("No se pudo validar la respuesta de Google.")

    id_token_bruto = token_google.get("id_token") if isinstance(token_google, dict) else None
    if not id_token_bruto:
        return _redirigir_con_error("Google no devolvió una credencial válida.")

    try:
        informacion_google = google_id_token.verify_oauth2_token(
            id_token_bruto, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        return _redirigir_con_error("La credencial de Google no es válida o expiró.")

    correo = informacion_google.get("email")
    nombre = informacion_google.get("name")
    google_sub = informacion_google.get("sub")
    if not correo or not informacion_google.get("email_verified", False):
        return _redirigir_con_error("Google no devolvió un correo verificado.")

    try:
        usuario = auth_service.authenticate_google(db, correo, nombre, google_sub)
    except ValueError as error_autenticacion:
        return _redirigir_con_error(str(error_autenticacion))

    token = create_access_token(data={"sub": str(usuario.id), "rol": usuario.rol.value})

    respuesta = RedirectResponse(
        url=f"{FRONTEND_URL}/#access_token={token}",
        status_code=status.HTTP_302_FOUND,
    )
    respuesta.delete_cookie(OAUTH_STATE_COOKIE)
    return respuesta


@router.get("/me", response_model=schemas.UsuarioOut, summary="Usuario autenticado actual")
def me(usuario_actual: models.Usuario = Depends(get_current_user)):
    return usuario_actual