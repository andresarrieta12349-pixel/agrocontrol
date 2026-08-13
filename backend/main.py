"""
Main FastAPI Application for AgroControl Pro
Backend API for agricultural management system
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import database
import models
from config import settings
from routers import auth_router, inputs_router, livestock_router, machinery_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AgroControl Pro - Agricultural Management System",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    database.init_db()
    print("✓ Database initialized")
    print(f"✓ {settings.APP_NAME} API starting...")
    print(f"✓ Docs available at http://{settings.HOST}:{settings.PORT}/api/docs")


# Include routers
app.include_router(auth_router)
app.include_router(inputs_router)
app.include_router(livestock_router)
app.include_router(machinery_router)


# ============================================================================
# HEALTH CHECK & INFO ENDPOINTS
# ============================================================================
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/api/docs",
        "openapi": "/api/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# DASHBOARD/STATS ENDPOINTS
# ============================================================================
@app.get("/api/stats")
async def get_stats(current_user = None):
    """
    Get dashboard statistics
    Note: Requires authentication (implement with get_current_user)
    """
    return {
        "insumos_count": 0,
        "livestock_count": 0,
        "machinery_count": 0,
        "recent_activities": []
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
