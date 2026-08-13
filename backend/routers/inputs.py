"""
Inputs (Insumos/Inventory) Router for AgroControl Pro
CRUD operations for agricultural inputs/supplies
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/insumos", tags=["insumos"])


@router.get("/", response_model=List[schemas.InsumoResponse])
def list_insumos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all insumos for current user
    """
    insumos = crud.get_insumos(db, skip=skip, limit=limit, user_id=current_user.id_usuario)
    return insumos


@router.get("/count", response_model=schemas.InsumoCountResponse)
def count_insumos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get count of insumos for current user
    """
    count = crud.get_insumos_count(db, user_id=current_user.id_usuario)
    return {"count": count}


@router.get("/{insumo_id}", response_model=schemas.InsumoResponse)
def get_insumo(
    insumo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get specific insumo by ID
    """
    insumo = crud.get_insumo(db, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo not found")
    
    if insumo.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return insumo


@router.post("/", response_model=schemas.InsumoResponse, status_code=status.HTTP_201_CREATED)
def create_insumo(
    insumo: schemas.InsumoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new insumo
    """
    db_insumo = crud.create_insumo(db, insumo, user_id=current_user.id_usuario)
    if not db_insumo:
        raise HTTPException(status_code=400, detail="Failed to create insumo")
    return db_insumo


@router.put("/{insumo_id}", response_model=schemas.InsumoResponse)
def update_insumo(
    insumo_id: int,
    insumo_update: schemas.InsumoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an insumo
    """
    insumo = crud.get_insumo(db, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo not found")
    
    if insumo.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_insumo = crud.update_insumo(db, insumo_id, insumo_update)
    return updated_insumo


@router.delete("/{insumo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insumo(
    insumo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an insumo
    """
    insumo = crud.get_insumo(db, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo not found")
    
    if insumo.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = crud.delete_insumo(db, insumo_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete insumo")
