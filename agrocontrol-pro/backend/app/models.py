"""
models.py
---------
Modelos SQLAlchemy (ORM) para AgroControl Pro.
Cubre: Usuarios/Autenticación, Administración (Fincas, Lotes, Proveedores, Pastos),
Inventario (Bodegas, Productos, Kardex) y Producción Agrícola
(Ciclos, Actividades, Cosechas) + Alertas para el dashboard.
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------
class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    SUPERVISOR = "supervisor"


class TipoMovimiento(str, enum.Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"


class EstadoCiclo(str, enum.Enum):
    PLANIFICADO = "planificado"
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class SeveridadAlerta(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    CRITICA = "critica"


# ---------------------------------------------------------------------------
# AUTENTICACIÓN / USUARIOS
# ---------------------------------------------------------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    nombre_usuario = Column(String(100), unique=True, index=True, nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=True)
    telefono = Column(String(30), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.OPERADOR, nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# ADMINISTRACIÓN: FINCAS, LOTES, PROVEEDORES, POTREROS, PASTOS
# ---------------------------------------------------------------------------
class Finca(Base):
    __tablename__ = "fincas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    ubicacion = Column(String(255), nullable=True)
    area_hectareas = Column(Float, default=0.0)
    responsable = Column(String(150), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    lotes = relationship("Lote", back_populates="finca", cascade="all, delete-orphan")


class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    area_hectareas = Column(Float, default=0.0)
    tipo_cultivo = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)

    finca = relationship("Finca", back_populates="lotes")
    ciclos = relationship("CicloProductivo", back_populates="lote")
    potreros = relationship("Potrero", back_populates="lote", cascade="all, delete-orphan")


class Potrero(Base):
    __tablename__ = "potreros"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    capacidad_animales = Column(Integer, nullable=False, default=0)
    tipo_pasto = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    lote = relationship("Lote", back_populates="potreros")
    animales = relationship("Animal", back_populates="potrero")


class Pasto(Base):
    __tablename__ = "pastos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)


class Animal(Base):
    __tablename__ = "animales"

    id = Column(Integer, primary_key=True, index=True)
    arete = Column(String(50), unique=True, index=True, nullable=False)
    peso_kg = Column(Float, nullable=False, default=0.0)
    estado_salud = Column(String(50), nullable=False, default="saludable")
    potrero_id = Column(Integer, ForeignKey("potreros.id"), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    potrero = relationship("Potrero", back_populates="animales")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(50), unique=True, nullable=True)
    contacto = Column(String(150), nullable=True)
    telefono = Column(String(30), nullable=True)
    correo = Column(String(150), nullable=True)
    direccion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# INVENTARIO: BODEGAS, PRODUCTOS, KARDEX
# ---------------------------------------------------------------------------
class Bodega(Base):
    __tablename__ = "bodegas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    ubicacion = Column(String(255), nullable=True)
    finca_id = Column(Integer, ForeignKey("fincas.id"), nullable=True)
    activo = Column(Boolean, default=True)

    movimientos = relationship("MovimientoInventario", back_populates="bodega")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    categoria = Column(String(100), nullable=True)
    unidad_medida = Column(String(30), nullable=False, default="unidad")
    stock_minimo = Column(Float, default=0.0)
    stock_actual = Column(Float, default=0.0)
    precio_unitario = Column(Float, default=0.0)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    proveedor = relationship("Proveedor")
    movimientos = relationship("MovimientoInventario", back_populates="producto")

    @property
    def en_stock_critico(self) -> bool:
        return self.stock_actual <= self.stock_minimo


class MovimientoInventario(Base):
    """Kardex: registra cada entrada/salida/ajuste de inventario."""
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False)
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    cantidad = Column(Float, nullable=False)
    costo_unitario = Column(Float, default=0.0)
    referencia = Column(String(150), nullable=True)
    observaciones = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    producto = relationship("Producto", back_populates="movimientos")
    bodega = relationship("Bodega", back_populates="movimientos")
    usuario = relationship("Usuario")


# ---------------------------------------------------------------------------
# PRODUCCIÓN AGRÍCOLA
# ---------------------------------------------------------------------------
class CicloProductivo(Base):
    __tablename__ = "ciclos_productivos"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    cultivo = Column(String(100), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_estimada_cosecha = Column(Date, nullable=True)
    fecha_fin_real = Column(Date, nullable=True)
    estado = Column(Enum(EstadoCiclo), default=EstadoCiclo.PLANIFICADO)
    rendimiento_esperado_kg = Column(Float, default=0.0)
    creado_en = Column(DateTime, default=datetime.utcnow)

    lote = relationship("Lote", back_populates="ciclos")
    actividades = relationship("ActividadDiaria", back_populates="ciclo", cascade="all, delete-orphan")
    cosechas = relationship("Cosecha", back_populates="ciclo", cascade="all, delete-orphan")


class ActividadDiaria(Base):
    __tablename__ = "actividades_diarias"

    id = Column(Integer, primary_key=True, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_productivos.id"), nullable=False)
    fecha = Column(Date, nullable=False, default=datetime.utcnow)
    tipo_actividad = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    responsable = Column(String(150), nullable=True)
    horas_trabajo = Column(Float, default=0.0)
    insumos_utilizados = Column(String(255), nullable=True)

    ciclo = relationship("CicloProductivo", back_populates="actividades")


class Cosecha(Base):
    __tablename__ = "cosechas"

    id = Column(Integer, primary_key=True, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos_productivos.id"), nullable=False)
    fecha = Column(Date, nullable=False, default=datetime.utcnow)
    cantidad_kg = Column(Float, nullable=False)
    calidad = Column(String(50), nullable=True)
    observaciones = Column(Text, nullable=True)

    ciclo = relationship("CicloProductivo", back_populates="cosechas")


# ---------------------------------------------------------------------------
# ALERTAS
# ---------------------------------------------------------------------------
class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    severidad = Column(Enum(SeveridadAlerta), default=SeveridadAlerta.MEDIA)
    modulo = Column(String(50), nullable=True)
    resuelta = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)