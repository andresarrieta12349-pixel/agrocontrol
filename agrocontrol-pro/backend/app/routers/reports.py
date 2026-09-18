"""
routers/reports.py
-------------------
Módulo de Reportes: resúmenes de inventario, movimientos de kardex,
producción agrícola y un reporte general para exportar o consultar
desde el panel de Reportes.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


# ---------------------------------------------------------------------------
# REPORTE DE INVENTARIO
# ---------------------------------------------------------------------------
@router.get("/inventario", summary="Reporte de estado de inventario")
def reporte_inventario(
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    productos = db.query(models.Producto).filter(models.Producto.activo.is_(True)).all()

    detalle = [
        {
            "id": p.id,
            "codigo": p.codigo,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "unidad_medida": p.unidad_medida,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "en_stock_critico": p.en_stock_critico,
            "precio_unitario": p.precio_unitario,
            "valor_total": round(p.stock_actual * p.precio_unitario, 2),
        }
        for p in productos
    ]

    return {
        "total_productos": len(detalle),
        "productos_stock_critico": sum(1 for p in detalle if p["en_stock_critico"]),
        "valor_total_inventario": round(sum(p["valor_total"] for p in detalle), 2),
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# REPORTE DE MOVIMIENTOS (KARDEX)
# ---------------------------------------------------------------------------
@router.get("/movimientos", summary="Reporte de movimientos de inventario")
def reporte_movimientos(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    producto_id: Optional[int] = None,
    bodega_id: Optional[int] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.MovimientoInventario)

    if fecha_inicio:
        query = query.filter(models.MovimientoInventario.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.MovimientoInventario.fecha <= fecha_fin)
    if producto_id:
        query = query.filter(models.MovimientoInventario.producto_id == producto_id)
    if bodega_id:
        query = query.filter(models.MovimientoInventario.bodega_id == bodega_id)

    movimientos = query.order_by(models.MovimientoInventario.fecha.desc()).all()

    total_entradas = sum(m.cantidad for m in movimientos if m.tipo == models.TipoMovimiento.ENTRADA)
    total_salidas = sum(m.cantidad for m in movimientos if m.tipo == models.TipoMovimiento.SALIDA)

    detalle = [
        {
            "id": m.id,
            "fecha": m.fecha,
            "producto": m.producto.nombre if m.producto else None,
            "bodega": m.bodega.nombre if m.bodega else None,
            "tipo": m.tipo,
            "cantidad": m.cantidad,
            "costo_unitario": m.costo_unitario,
            "referencia": m.referencia,
        }
        for m in movimientos
    ]

    return {
        "total_movimientos": len(detalle),
        "total_entradas": total_entradas,
        "total_salidas": total_salidas,
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# REPORTE DE PRODUCCIÓN AGRÍCOLA
# ---------------------------------------------------------------------------
@router.get("/produccion", summary="Reporte de producción agrícola")
def reporte_produccion(
    lote_id: Optional[int] = None,
    estado: Optional[models.EstadoCiclo] = None,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.CicloProductivo)
    if lote_id:
        query = query.filter(models.CicloProductivo.lote_id == lote_id)
    if estado:
        query = query.filter(models.CicloProductivo.estado == estado)

    ciclos = query.order_by(models.CicloProductivo.fecha_inicio.desc()).all()

    detalle = []
    for c in ciclos:
        total_cosechado = sum(cos.cantidad_kg for cos in c.cosechas)
        detalle.append({
            "id": c.id,
            "nombre": c.nombre,
            "cultivo": c.cultivo,
            "lote": c.lote.nombre if c.lote else None,
            "estado": c.estado,
            "fecha_inicio": c.fecha_inicio,
            "fecha_estimada_cosecha": c.fecha_estimada_cosecha,
            "rendimiento_esperado_kg": c.rendimiento_esperado_kg,
            "total_cosechado_kg": total_cosechado,
            "numero_actividades": len(c.actividades),
        })

    return {
        "total_ciclos": len(detalle),
        "ciclos_activos": sum(1 for c in detalle if c["estado"] == models.EstadoCiclo.ACTIVO),
        "total_cosechado_kg": round(sum(c["total_cosechado_kg"] for c in detalle), 2),
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# REPORTE GENERAL (RESUMEN EJECUTIVO)
# ---------------------------------------------------------------------------
@router.get("/general", summary="Reporte general del sistema")
def reporte_general(
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    total_fincas = db.query(models.Finca).filter(models.Finca.activo.is_(True)).count()
    total_lotes = db.query(models.Lote).filter(models.Lote.activo.is_(True)).count()
    total_animales = db.query(models.Animal).filter(models.Animal.activo.is_(True)).count()
    ciclos_activos = (
        db.query(models.CicloProductivo)
        .filter(models.CicloProductivo.estado == models.EstadoCiclo.ACTIVO)
        .count()
    )

    productos = db.query(models.Producto).filter(models.Producto.activo.is_(True)).all()
    valor_inventario = round(sum(p.stock_actual * p.precio_unitario for p in productos), 2)
    productos_criticos = sum(1 for p in productos if p.en_stock_critico)

    alertas_criticas = (
        db.query(models.Alerta)
        .filter(
            models.Alerta.severidad == models.SeveridadAlerta.CRITICA,
            models.Alerta.resuelta.is_(False),
        )
        .count()
    )

    return {
        "total_fincas": total_fincas,
        "total_lotes": total_lotes,
        "total_animales": total_animales,
        "ciclos_activos": ciclos_activos,
        "valor_total_inventario": valor_inventario,
        "productos_stock_critico": productos_criticos,
        "alertas_criticas": alertas_criticas,
    }