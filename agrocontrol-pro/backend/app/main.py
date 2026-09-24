"""
main.py
-------
Punto de entrada de la API de AgroControl Pro (FastAPI).

- Crea las tablas en la base de datos (para entornos donde no se use Alembic).
- Registra todos los routers de los módulos del sistema.
- Habilita CORS SOLO para los orígenes listados en CORS_ORIGINS.
- Agrega cabeceras de seguridad a todas las respuestas.
- En producción (ENVIRONMENT=production) desactiva la documentación
  interactiva (/docs, /redoc), que no debe ser pública.
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth_router, dashboard, inventory, production, admin, reports, gastos
from app.security import ES_PRODUCCION, instalar_cabeceras_seguridad

logger = logging.getLogger("agrocontrol.main")

app = FastAPI(
    title="AgroControl Pro API",
    description=(
        "API B2B para gestión agrícola integral: autenticación, dashboard "
        "operativo, inventario y bodegas, producción agrícola y "
        "administración de fincas, lotes, proveedores y usuarios."
    ),
    version="1.0.0",
    docs_url=None if ES_PRODUCCION else "/docs",
    redoc_url=None if ES_PRODUCCION else "/redoc",
    openapi_url=None if ES_PRODUCCION else "/openapi.json",
)

# ---------------------------------------------------------------------------
# Cabeceras de seguridad (se instala primero para que CORS quede por fuera)
# ---------------------------------------------------------------------------
instalar_cabeceras_seguridad(app)

# ---------------------------------------------------------------------------
# CORS: lista explícita de orígenes. Nunca "*" ni regex abierta, porque con
# credenciales habilitadas eso permitiría que CUALQUIER sitio web lea datos
# de la API en nombre de un usuario autenticado.
# ---------------------------------------------------------------------------
_ORIGENES_POR_DEFECTO = "http://localhost:8080,http://127.0.0.1:8080"
_origenes_crudos = os.getenv("CORS_ORIGINS", _ORIGENES_POR_DEFECTO)
origins = [o.strip().rstrip("/") for o in _origenes_crudos.split(",") if o.strip() and o.strip() != "*"]
if "*" in _origenes_crudos:
    logger.warning("CORS_ORIGINS contiene '*': se ignora. Lista los dominios permitidos explícitamente.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------------------------
# Eventos de arranque
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health", tags=["Sistema"], summary="Estado del servicio")
def health_check():
    return {"status": "ok", "servicio": "AgroControl Pro API"}


# ---------------------------------------------------------------------------
# Routers de los módulos del sistema
# ---------------------------------------------------------------------------
app.include_router(auth_router.router)
app.include_router(dashboard.router)
app.include_router(inventory.router)
app.include_router(production.router)
app.include_router(admin.router)
app.include_router(reports.router)
app.include_router(gastos.router)
