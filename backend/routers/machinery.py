"""
Machinery (Maquinaria) Router for AgroControl Pro
CRUD operations for agricultural equipment management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/machinery", tags=["machinery"])


@router.get("/", response_model=List[schemas.MaquinariaResponse])
def list_maquinarias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all equipment for current user
    """
    maquinarias = crud.get_maquinarias(db, skip=skip, limit=limit, user_id=current_user.id_usuario)
    return maquinarias


@router.get("/count", response_model=schemas.MaquinariaCountResponse)
def count_maquinarias(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get count of equipment for current user
    """
    count = crud.get_maquinarias_count(db, user_id=current_user.id_usuario)
    return {"count": count}


@router.get("/{maquinaria_id}", response_model=schemas.MaquinariaResponse)
def get_maquinaria(
    maquinaria_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get specific equipment by ID
    """
    maquinaria = crud.get_maquinaria(db, maquinaria_id)
    if not maquinaria:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if maquinaria.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return maquinaria


@router.post("/", response_model=schemas.MaquinariaResponse, status_code=status.HTTP_201_CREATED)
def create_maquinaria(
    maquinaria: schemas.MaquinariaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new equipment
    """
    db_maquinaria = crud.create_maquinaria(db, maquinaria, user_id=current_user.id_usuario)
    if not db_maquinaria:
        raise HTTPException(status_code=400, detail="Equipment code already exists or failed to create")
    return db_maquinaria


@router.put("/{maquinaria_id}", response_model=schemas.MaquinariaResponse)
def update_maquinaria(
    maquinaria_id: int,
    maquinaria_update: schemas.MaquinariaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update equipment
    """
    maquinaria = crud.get_maquinaria(db, maquinaria_id)
    if not maquinaria:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if maquinaria.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_maquinaria = crud.update_maquinaria(db, maquinaria_id, maquinaria_update)
    return updated_maquinaria


@router.delete("/{maquinaria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maquinaria(
    maquinaria_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete equipment
    """
    maquinaria = crud.get_maquinaria(db, maquinaria_id)
    if not maquinaria:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if maquinaria.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = crud.delete_maquinaria(db, maquinaria_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete equipment")


# ============================================================================
# MANTENIMIENTO ENDPOINTS (Maintenance tracking)
# ============================================================================
@router.post("/{maquinaria_id}/mantenimientos", response_model=schemas.MantenimientoResponse, status_code=status.HTTP_201_CREATED)
def add_mantenimiento(
    maquinaria_id: int,
    mantenimiento: schemas.MantenimientoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add a new maintenance record for equipment
    """
    maquinaria = crud.get_maquinaria(db, maquinaria_id)
    if not maquinaria:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if maquinaria.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_mantenimiento = crud.create_mantenimiento(db, mantenimiento)
    return db_mantenimiento


@router.get("/{maquinaria_id}/mantenimientos", response_model=List[schemas.MantenimientoResponse])
def get_mantenimientos(
    maquinaria_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all maintenance records for equipment
    """
    maquinaria = crud.get_maquinaria(db, maquinaria_id)
    if not maquinaria:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if maquinaria.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    mantenimientos = crud.get_mantenimientos_by_equipo(db, maquinaria_id)
    return mantenimientos
