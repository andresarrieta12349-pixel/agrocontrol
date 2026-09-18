"""
main.py
-------
Punto de entrada de la API de AgroControl Pro (FastAPI).

- Crea las tablas en la base de datos (para entornos donde no se use Alembic).
- Registra todos los routers de los módulos del sistema.
- Habilita CORS para que el frontend (servido por Nginx en otro puerto)
  pueda consumir la API.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth_router, dashboard, inventory, production, admin, reports

app = FastAPI(
    title="AgroControl Pro API",
    description=(
        "API B2B para gestión agrícola integral: autenticación, dashboard "
        "operativo, inventario y bodegas, producción agrícola y "
        "administración de fincas, lotes, proveedores y usuarios."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
origins_env = os.getenv("CORS_ORIGINS", "*")
origins = ["*"] if origins_env.strip() == "*" else [o.strip() for o in origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins_env.strip() != "*" else [],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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