"""
routers/inventory.py
----------------------
Módulo de Inventario y Bodegas: CRUD de bodegas, productos/insumos y
registro de movimientos de kardex (entradas, salidas, ajustes), con
actualización automática de stock y generación de alertas por stock
crítico.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/inventario", tags=["Inventario y Bodegas"])


# ---------------------------------------------------------------------------
# BODEGAS
# ---------------------------------------------------------------------------
@router.get("/bodegas", response_model=List[schemas.BodegaOut])
def listar_bodegas(
    incluir_inactivas: bool = True,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.Bodega)
    if not incluir_inactivas:
        query = query.filter(models.Bodega.activo.is_(True))
    return query.order_by(models.Bodega.nombre).all()


@router.post("/bodegas", response_model=schemas.BodegaOut, status_code=status.HTTP_201_CREATED)
def crear_bodega(
    payload: schemas.BodegaCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    bodega = models.Bodega(**payload.model_dump())
    db.add(bodega)
    db.commit()
    db.refresh(bodega)
    return bodega


@router.put("/bodegas/{bodega_id}", response_model=schemas.BodegaOut)
def actualizar_bodega(
    bodega_id: int,
    payload: schemas.BodegaUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    bodega = db.query(models.Bodega).filter(models.Bodega.id == bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(bodega, campo, valor)
    db.commit()
    db.refresh(bodega)
    return bodega


@router.delete("/bodegas/{bodega_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(
    bodega_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    bodega = db.query(models.Bodega).filter(models.Bodega.id == bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    bodega.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# PRODUCTOS / INSUMOS
# ---------------------------------------------------------------------------
@router.get("/productos", response_model=List[schemas.ProductoOut])
def listar_productos(
    stock_critico: Optional[bool] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.Producto).filter(models.Producto.activo.is_(True))
    productos = query.order_by(models.Producto.nombre).all()
    if stock_critico is True:
        productos = [p for p in productos if p.en_stock_critico]
    return productos


@router.post("/productos", response_model=schemas.ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    payload: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    existente = db.query(models.Producto).filter(models.Producto.codigo == payload.codigo).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un producto con ese código")
    producto = models.Producto(**payload.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/productos/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    payload: schemas.ProductoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# MOVIMIENTOS DE KARDEX
# ---------------------------------------------------------------------------
def _generar_alerta_si_critico(db: Session, producto: models.Producto) -> None:
    if producto.en_stock_critico:
        alerta = models.Alerta(
            titulo=f"Stock crítico: {producto.nombre}",
            mensaje=(
                f"El producto '{producto.nombre}' ({producto.codigo}) tiene "
                f"{producto.stock_actual} {producto.unidad_medida} en stock, "
                f"por debajo del mínimo de {producto.stock_minimo}."
            ),
            severidad=models.SeveridadAlerta.CRITICA,
            modulo="inventario",
        )
        db.add(alerta)
        db.commit()


@router.get("/movimientos", response_model=List[schemas.MovimientoInventarioOut])
def listar_movimientos(
    producto_id: Optional[int] = None,
    bodega_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.MovimientoInventario)
    if producto_id:
        query = query.filter(models.MovimientoInventario.producto_id == producto_id)
    if bodega_id:
        query = query.filter(models.MovimientoInventario.bodega_id == bodega_id)
    return query.order_by(models.MovimientoInventario.fecha.desc()).limit(200).all()


@router.post(
    "/movimientos",
    response_model=schemas.MovimientoInventarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimiento de kardex (entrada/salida/ajuste)",
)
def crear_movimiento(
    payload: schemas.MovimientoInventarioCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    producto = db.query(models.Producto).filter(models.Producto.id == payload.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    bodega = db.query(models.Bodega).filter(models.Bodega.id == payload.bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")

    if payload.tipo == models.TipoMovimiento.SALIDA and payload.cantidad > producto.stock_actual:
        raise HTTPException(
            status_code=400,
            detail="La cantidad de salida supera el stock actual disponible",
        )

    movimiento = models.MovimientoInventario(
        **payload.model_dump(), usuario_id=usuario_actual.id
    )
    db.add(movimiento)

    if payload.tipo == models.TipoMovimiento.ENTRADA:
        producto.stock_actual += payload.cantidad
    elif payload.tipo == models.TipoMovimiento.SALIDA:
        producto.stock_actual -= payload.cantidad
    elif payload.tipo == models.TipoMovimiento.AJUSTE:
        producto.stock_actual = payload.cantidad

    db.commit()
    db.refresh(movimiento)

    _generar_alerta_si_critico(db, producto)
    return movimiento
