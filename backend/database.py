"""
Database configuration for AgroControl Pro
SQLAlchemy + MySQL setup with connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/agrocontrol_pro"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
    pool_recycle=3600
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    """
    Dependency function to get database session.
    Usage in routes: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Call this function on startup to create tables if they don't exist.
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables. USE WITH CAUTION!
    Only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
