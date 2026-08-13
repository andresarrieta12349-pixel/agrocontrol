"""
Livestock (Ganado) Router for AgroControl Pro
CRUD operations for animal management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/livestock", tags=["livestock"])


@router.get("/", response_model=List[schemas.GanadoResponse])
def list_ganados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all animals for current user
    """
    ganados = crud.get_ganados(db, skip=skip, limit=limit, user_id=current_user.id_usuario)
    return ganados


@router.get("/count", response_model=schemas.GanadoCountResponse)
def count_ganados(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get count of animals for current user
    """
    count = crud.get_ganados_count(db, user_id=current_user.id_usuario)
    return {"count": count}


@router.get("/{ganado_id}", response_model=schemas.GanadoResponse)
def get_ganado(
    ganado_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get specific animal by ID
    """
    ganado = crud.get_ganado(db, ganado_id)
    if not ganado:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if ganado.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return ganado


@router.post("/", response_model=schemas.GanadoResponse, status_code=status.HTTP_201_CREATED)
def create_ganado(
    ganado: schemas.GanadoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new animal
    """
    db_ganado = crud.create_ganado(db, ganado, user_id=current_user.id_usuario)
    if not db_ganado:
        raise HTTPException(status_code=400, detail="Animal ID already exists or failed to create")
    return db_ganado


@router.put("/{ganado_id}", response_model=schemas.GanadoResponse)
def update_ganado(
    ganado_id: int,
    ganado_update: schemas.GanadoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an animal
    """
    ganado = crud.get_ganado(db, ganado_id)
    if not ganado:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if ganado.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_ganado = crud.update_ganado(db, ganado_id, ganado_update)
    return updated_ganado


@router.delete("/{ganado_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ganado(
    ganado_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete an animal
    """
    ganado = crud.get_ganado(db, ganado_id)
    if not ganado:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if ganado.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = crud.delete_ganado(db, ganado_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete animal")


# ============================================================================
# PESAJE ENDPOINTS (Weight tracking)
# ============================================================================
@router.post("/{ganado_id}/pesajes", response_model=schemas.PesajeResponse, status_code=status.HTTP_201_CREATED)
def add_pesaje(
    ganado_id: int,
    pesaje: schemas.PesajeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add a new weight measurement for an animal
    """
    ganado = crud.get_ganado(db, ganado_id)
    if not ganado:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if ganado.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_pesaje = crud.create_pesaje(db, pesaje)
    return db_pesaje


@router.get("/{ganado_id}/pesajes", response_model=List[schemas.PesajeResponse])
def get_pesajes(
    ganado_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all weight measurements for an animal
    """
    ganado = crud.get_ganado(db, ganado_id)
    if not ganado:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    if ganado.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    pesajes = crud.get_pesajes_by_animal(db, ganado_id)
    return pesajes
