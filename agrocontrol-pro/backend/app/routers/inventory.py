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


def _validar_finca_activa(db: Session, finca_id: Optional[int]) -> None:
    if finca_id is None:
        return
    if not db.query(models.Finca).filter(models.Finca.id == finca_id, models.Finca.activo.is_(True)).first():
        raise HTTPException(status_code=400, detail="La finca indicada no existe o está inactiva.")


def _validar_proveedor(db: Session, proveedor_id: Optional[int]) -> None:
    if proveedor_id is None:
        return
    if not db.get(models.Proveedor, proveedor_id):
        raise HTTPException(status_code=400, detail="El proveedor indicado no existe.")


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
    # Validación estricta: no se permite crear una bodega sin una finca
    # activa registrada y seleccionada. Esto respalda en el servidor la
    # validación que ya hace el frontend en el selector superior.
    finca = (
        db.query(models.Finca)
        .filter(models.Finca.id == payload.finca_id, models.Finca.activo.is_(True))
        .first()
    )
    if not finca:
        raise HTTPException(
            status_code=400,
            detail="Debes registrar y seleccionar una finca activa antes de crear una bodega.",
        )

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
    cambios = payload.model_dump(exclude_unset=True)
    if cambios.get("finca_id") is not None:
        _validar_finca_activa(db, cambios["finca_id"])
    for campo, valor in cambios.items():
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
    _validar_proveedor(db, payload.proveedor_id)
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
    cambios = payload.model_dump(exclude_unset=True)
    _validar_proveedor(db, cambios.get("proveedor_id"))
    for campo, valor in cambios.items():
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
        titulo = f"Stock crítico: {producto.nombre}"
        # Evita inundar la tabla de alertas: una sola alerta abierta por producto.
        ya_abierta = (
            db.query(models.Alerta.id)
            .filter(
                models.Alerta.modulo == "inventario",
                models.Alerta.titulo == titulo,
                models.Alerta.resuelta.is_(False),
            )
            .first()
        )
        if ya_abierta:
            return
        alerta = models.Alerta(
            titulo=titulo,
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
    # with_for_update bloquea la fila del producto hasta el commit: evita que dos
    # salidas simultáneas lean el mismo stock y lo dejen en negativo.
    producto = (
        db.query(models.Producto)
        .filter(models.Producto.id == payload.producto_id)
        .with_for_update()
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not producto.activo:
        raise HTTPException(status_code=400, detail="El producto está inactivo")

    bodega = db.query(models.Bodega).filter(models.Bodega.id == payload.bodega_id).first()
    if not bodega:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    if not bodega.activo:
        raise HTTPException(status_code=400, detail="La bodega está inactiva")

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