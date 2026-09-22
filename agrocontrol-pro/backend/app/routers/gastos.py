"""
routers/gastos.py
------------------
Registro de gastos de la finca (Insumos, Mano de obra, Maquinaria, Otros).
Estos gastos son los que alimentan el gráfico circular del Dashboard.
"""
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/gastos", tags=["Gastos"])


def fecha_desde_periodo(periodo: str) -> Optional[date]:
    """Convierte el período del selector del Dashboard en una fecha de inicio."""
    hoy = date.today()
    if periodo == "mes":
        return hoy.replace(day=1)
    if periodo == "trimestre":
        return hoy - timedelta(days=90)
    if periodo == "anio":
        return date(hoy.year, 1, 1)
    return None  # "todo": sin límite de fecha


def _validar_finca(db: Session, finca_id: Optional[int]) -> None:
    if finca_id is not None and db.get(models.Finca, finca_id) is None:
        raise HTTPException(status_code=404, detail="La finca seleccionada no existe.")


def _obtener_gasto(db: Session, gasto_id: int) -> models.Gasto:
    gasto = db.get(models.Gasto, gasto_id)
    if gasto is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado.")
    return gasto


@router.get("", response_model=List[schemas.GastoOut], summary="Listar gastos")
def listar_gastos(
    periodo: str = Query("mes", description="mes | trimestre | anio | todo"),
    limite: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    consulta = db.query(models.Gasto)
    desde = fecha_desde_periodo(periodo)
    if desde is not None:
        consulta = consulta.filter(models.Gasto.fecha >= desde)
    return (
        consulta.order_by(models.Gasto.fecha.desc(), models.Gasto.id.desc())
        .limit(limite)
        .all()
    )


@router.post("", response_model=schemas.GastoOut, status_code=status.HTTP_201_CREATED, summary="Registrar gasto")
def crear_gasto(
    datos: schemas.GastoCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    _validar_finca(db, datos.finca_id)
    gasto = models.Gasto(**datos.model_dump(), usuario_id=usuario_actual.id)
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto


@router.put("/{gasto_id}", response_model=schemas.GastoOut, summary="Editar gasto")
def actualizar_gasto(
    gasto_id: int,
    datos: schemas.GastoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    gasto = _obtener_gasto(db, gasto_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "finca_id" in cambios:
        _validar_finca(db, cambios["finca_id"])
    for campo, valor in cambios.items():
        setattr(gasto, campo, valor)
    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Borrar gasto")
def borrar_gasto(
    gasto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    gasto = _obtener_gasto(db, gasto_id)
    db.delete(gasto)
    db.commit()