"""
database.py
-----------
Configuración central de SQLAlchemy para AgroControl Pro.
Soporta PostgreSQL (recomendado en producción, vía docker-compose) y
SQLite (fallback automático para desarrollo local sin Docker).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Si no se define DATABASE_URL, se usa SQLite embebido como fallback
# para poder levantar el proyecto sin depender de Postgres.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agrocontrol_pro.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
