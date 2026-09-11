"""
routers/production.py
------------------------
Módulo de Producción Agrícola: ciclos productivos, registro de
actividades diarias y cosechas.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/produccion", tags=["Producción Agrícola"])


# ---------------------------------------------------------------------------
# CICLOS PRODUCTIVOS
# ---------------------------------------------------------------------------
@router.get("/ciclos", response_model=List[schemas.CicloProductivoOut])
def listar_ciclos(
    estado: Optional[models.EstadoCiclo] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.CicloProductivo)
    if estado:
        query = query.filter(models.CicloProductivo.estado == estado)
    return query.order_by(models.CicloProductivo.fecha_inicio.desc()).all()


@router.post("/ciclos", response_model=schemas.CicloProductivoOut, status_code=status.HTTP_201_CREATED)
def crear_ciclo(
    payload: schemas.CicloProductivoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    lote = db.query(models.Lote).filter(models.Lote.id == payload.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    ciclo = models.CicloProductivo(**payload.model_dump(), estado=models.EstadoCiclo.PLANIFICADO)
    db.add(ciclo)
    db.commit()
    db.refresh(ciclo)
    return ciclo


@router.put("/ciclos/{ciclo_id}", response_model=schemas.CicloProductivoOut)
def actualizar_ciclo(
    ciclo_id: int,
    payload: schemas.CicloProductivoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    ciclo = db.query(models.CicloProductivo).filter(models.CicloProductivo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo productivo no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(ciclo, campo, valor)
    db.commit()
    db.refresh(ciclo)
    return ciclo


@router.delete("/ciclos/{ciclo_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_ciclo(
    ciclo_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    ciclo = db.query(models.CicloProductivo).filter(models.CicloProductivo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo productivo no encontrado")
    ciclo.estado = models.EstadoCiclo.CANCELADO
    db.commit()
    return None


# ---------------------------------------------------------------------------
# ACTIVIDADES DIARIAS
# ---------------------------------------------------------------------------
@router.get("/actividades", response_model=List[schemas.ActividadDiariaOut])
def listar_actividades(
    ciclo_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.ActividadDiaria)
    if ciclo_id:
        query = query.filter(models.ActividadDiaria.ciclo_id == ciclo_id)
    return query.order_by(models.ActividadDiaria.fecha.desc()).all()


@router.post(
    "/actividades", response_model=schemas.ActividadDiariaOut, status_code=status.HTTP_201_CREATED
)
def crear_actividad(
    payload: schemas.ActividadDiariaCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    ciclo = db.query(models.CicloProductivo).filter(models.CicloProductivo.id == payload.ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo productivo no encontrado")

    # Marca el ciclo como activo automáticamente cuando se registra la primera actividad
    if ciclo.estado == models.EstadoCiclo.PLANIFICADO:
        ciclo.estado = models.EstadoCiclo.ACTIVO

    actividad = models.ActividadDiaria(**payload.model_dump())
    db.add(actividad)
    db.commit()
    db.refresh(actividad)
    return actividad


# ---------------------------------------------------------------------------
# COSECHAS
# ---------------------------------------------------------------------------
@router.get("/cosechas", response_model=List[schemas.CosechaOut])
def listar_cosechas(
    ciclo_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.Cosecha)
    if ciclo_id:
        query = query.filter(models.Cosecha.ciclo_id == ciclo_id)
    return query.order_by(models.Cosecha.fecha.desc()).all()


@router.post("/cosechas", response_model=schemas.CosechaOut, status_code=status.HTTP_201_CREATED)
def crear_cosecha(
    payload: schemas.CosechaCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    ciclo = db.query(models.CicloProductivo).filter(models.CicloProductivo.id == payload.ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=404, detail="Ciclo productivo no encontrado")

    cosecha = models.Cosecha(**payload.model_dump())
    db.add(cosecha)
    db.commit()
    db.refresh(cosecha)
    return cosecha
