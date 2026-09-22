"""
routers/dashboard.py
---------------------
Endpoint agregador para el Dashboard Operativo: KPIs de ciclos activos,
alertas críticas, stock crítico y series semanales de entradas/salidas
de inventario (kardex) para graficar con Chart.js.

Incluye también la distribución de gastos por categoría para el gráfico
circular del dashboard (Insumos, Mano de obra, Maquinaria, Otros), calculada
a partir de los gastos que se registran en la tabla "gastos".
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from app.routers.gastos import fecha_desde_periodo

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def calcular_gastos_por_categoria(db: Session, desde: Optional[date]) -> dict:
    """
    Suma los gastos registrados por categoría desde la fecha `desde`
    (None = todo el historial). Siempre devuelve las 4 categorías.
    """
    resultado = {categoria.value: 0.0 for categoria in models.CategoriaGasto}

    consulta = db.query(models.Gasto.categoria, func.sum(models.Gasto.monto))
    if desde is not None:
        consulta = consulta.filter(models.Gasto.fecha >= desde)

    for categoria, total in consulta.group_by(models.Gasto.categoria).all():
        clave = categoria.value if hasattr(categoria, "value") else str(categoria)
        resultado[clave] = round(float(total or 0), 2)
    return resultado


@router.get("/resumen", response_model=schemas.DashboardResumen, summary="Resumen operativo (KPIs)")
def resumen(
    periodo: str = Query("mes", description="Período del gráfico de gastos: mes | trimestre | anio | todo"),
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

    # --- Gastos por categoría (gráfico circular) ---
    gastos_por_categoria = calcular_gastos_por_categoria(db, fecha_desde_periodo(periodo))

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
        gastos_por_categoria=gastos_por_categoria,
    )