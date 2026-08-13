"""
FastAPI routers package for AgroControl Pro
"""

from .auth import router as auth_router
from .inputs import router as inputs_router
from .livestock import router as livestock_router
from .machinery import router as machinery_router

__all__ = [
    "auth_router",
    "inputs_router", 
    "livestock_router",
    "machinery_router"
]
