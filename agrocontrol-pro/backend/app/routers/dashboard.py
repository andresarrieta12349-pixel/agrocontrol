"""
routers/dashboard.py
---------------------
Endpoint agregador para el Dashboard Operativo: KPIs de ciclos activos,
alertas críticas, stock crítico y series semanales de entradas/salidas
de inventario (kardex) para graficar con Chart.js.
"""
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumen", response_model=schemas.DashboardResumen, summary="Resumen operativo (KPIs)")
def resumen(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(get_current_user),
):
    ciclos_activos = (
        db.query(func.count(models.CicloProductivo.id))
        .filter(models.CicloProductivo.estado == models.EstadoCiclo.ACTIVO)
        .scalar() or 0
    )
    ciclos_planificados = (
        db.query(func.count(models.CicloProductivo.id))
        .filter(models.CicloProductivo.estado == models.EstadoCiclo.PLANIFICADO)
        .scalar() or 0
    )
    alertas_criticas = (
        db.query(func.count(models.Alerta.id))
        .filter(
            models.Alerta.severidad == models.SeveridadAlerta.CRITICA,
            models.Alerta.resuelta.is_(False),
        )
        .scalar() or 0
    )

    productos = db.query(models.Producto).filter(models.Producto.activo.is_(True)).all()
    productos_stock_critico = sum(1 for p in productos if p.stock_actual <= p.stock_minimo)
    valor_inventario = sum(p.stock_actual * p.precio_unitario for p in productos)

    total_bodegas = db.query(func.count(models.Bodega.id)).filter(models.Bodega.activo.is_(True)).scalar() or 0
    total_fincas = db.query(func.count(models.Finca.id)).filter(models.Finca.activo.is_(True)).scalar() or 0

    # --- Serie semanal de entradas/salidas (últimas 8 semanas) ---
    hace_8_semanas = datetime.utcnow() - timedelta(weeks=8)
    movimientos = (
        db.query(models.MovimientoInventario)
        .filter(models.MovimientoInventario.fecha >= hace_8_semanas)
        .all()
    )

    semanas = defaultdict(lambda: {"entradas": 0.0, "salidas": 0.0})
    for mov in movimientos:
        etiqueta_semana = mov.fecha.strftime("Sem %W - %Y")
        if mov.tipo == models.TipoMovimiento.ENTRADA:
            semanas[etiqueta_semana]["entradas"] += mov.cantidad
        elif mov.tipo == models.TipoMovimiento.SALIDA:
            semanas[etiqueta_semana]["salidas"] += mov.cantidad

    serie_ordenada = sorted(semanas.items(), key=lambda item: item[0])
    movimientos_kardex_semanal = [
        schemas.SerieSemanal(semana=semana, entradas=datos["entradas"], salidas=datos["salidas"])
        for semana, datos in serie_ordenada
    ]

    alertas_recientes = (
        db.query(models.Alerta)
        .order_by(models.Alerta.creado_en.desc())
        .limit(6)
        .all()
    )

    return schemas.DashboardResumen(
        ciclos_activos=ciclos_activos,
        ciclos_planificados=ciclos_planificados,
        alertas_criticas=alertas_criticas,
        productos_stock_critico=productos_stock_critico,
        total_bodegas=total_bodegas,
        total_fincas=total_fincas,
        valor_inventario=round(valor_inventario, 2),
        movimientos_kardex_semanal=movimientos_kardex_semanal,
        alertas_recientes=alertas_recientes,
    )
