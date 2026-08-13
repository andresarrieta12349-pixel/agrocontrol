"""
SQLAlchemy Models for AgroControl Pro
Database models for all entities
"""

from database import Base
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


# Enums for status and other fields
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SECRETARY = "secretary"
    WORKER = "worker"


class OperationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"


class AnimalSex(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class AnimalHealth(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    REGULAR = "regular"
    SICK = "sick"


# ============================================================================
# USER MODEL
# ============================================================================
class User(Base):
    __tablename__ = "users"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default=UserRole.SECRETARY, nullable=False)
    fecha_registro = Column(Date, default=datetime.now, nullable=False)
    estado = Column(String(20), default=OperationStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    insumos = relationship("Insumo", back_populates="usuario")
    ganado = relationship("Ganado", back_populates="usuario")
    maquinaria = relationship("Maquinaria", back_populates="usuario")
    
    def __repr__(self):
        return f"<User {self.nombre_usuario}>"


# ============================================================================
# INSUMO MODEL (Inventario / Inputs)
# ============================================================================
class Insumo(Base):
    __tablename__ = "insumos"
    
    id_insumo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), index=True, nullable=False)
    tipo = Column(String(100), nullable=False)  # fertilizante, pesticida, fungicida, herbicida, semilla, otro
    cantidad = Column(Float, nullable=False)
    unidad = Column(String(50), nullable=False)  # kg, lt, u, bolsa, caneca
    precio = Column(Float, nullable=False)
    fecha = Column(Date, default=datetime.now, nullable=False)
    proveedor = Column(String(150), nullable=False)
    lote = Column(String(100), nullable=True)
    total = Column(Float, nullable=False)  # cantidad * precio
    estado = Column(String(20), default=OperationStatus.ACTIVE, nullable=False)
    
    # Foreign key
    id_usuario = Column(Integer, ForeignKey("users.id_usuario"), nullable=False)
    
    # Relationships
    usuario = relationship("User", back_populates="insumos")
    
    def __repr__(self):
        return f"<Insumo {self.nombre}>"


# ============================================================================
# GANADO MODEL (Livestock / Animals)
# ============================================================================
class Ganado(Base):
    __tablename__ = "ganado"
    
    id_animal = Column(Integer, primary_key=True, index=True)
    id_animal_str = Column(String(50), unique=True, index=True, nullable=False)
    nombre_animal = Column(String(150), nullable=False)
    tipo_animal = Column(String(100), nullable=False)  # bovino, porcino, ovino, caprino, equino, aviar
    raza = Column(String(100), nullable=False)
    sexo = Column(String(10), nullable=False)  # M o F
    edad = Column(Integer, nullable=False)  # in months
    peso = Column(Float, nullable=False)  # in kg
    fecha_nacimiento = Column(Date, nullable=False)
    estado_salud = Column(String(50), default=AnimalHealth.GOOD, nullable=False)
    valor_animal = Column(Float, nullable=False)
    fecha_registro = Column(Date, default=datetime.now, nullable=False)
    estado = Column(String(20), default=OperationStatus.ACTIVE, nullable=False)
    
    # Foreign key
    id_usuario = Column(Integer, ForeignKey("users.id_usuario"), nullable=False)
    
    # Relationships
    usuario = relationship("User", back_populates="ganado")
    pesajes = relationship("Pesaje", back_populates="animal")
    
    def __repr__(self):
        return f"<Ganado {self.nombre_animal}>"


# ============================================================================
# PESAJE MODEL (Weighing history)
# ============================================================================
class Pesaje(Base):
    __tablename__ = "pesajes"
    
    id_pesaje = Column(Integer, primary_key=True, index=True)
    id_animal = Column(Integer, ForeignKey("ganado.id_animal"), nullable=False)
    peso = Column(Float, nullable=False)
    fecha_pesaje = Column(Date, default=datetime.now, nullable=False)
    observaciones = Column(Text, nullable=True)
    
    # Relationships
    animal = relationship("Ganado", back_populates="pesajes")
    
    def __repr__(self):
        return f"<Pesaje {self.id_animal} - {self.peso}kg>"


# ============================================================================
# MAQUINARIA MODEL (Machinery / Equipment)
# ============================================================================
class Maquinaria(Base):
    __tablename__ = "maquinaria"
    
    id_equipo = Column(Integer, primary_key=True, index=True)
    codigo_equipo = Column(String(100), unique=True, index=True, nullable=False)
    nombre_equipo = Column(String(150), nullable=False)
    tipo_equipo = Column(String(100), nullable=False)  # tractor, cosechadora, arado, sembradora, pulverizador, rastrillo, otro
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    anno_fabricacion = Column(Integer, nullable=False)
    serie = Column(String(100), nullable=True)
    estado = Column(String(50), nullable=False)  # excelente, bueno, regular, mantenimiento, inoperativo
    horas_trabajo = Column(Float, default=0, nullable=False)
    valor_adquisicion = Column(Float, nullable=False)
    fecha_adquisicion = Column(Date, nullable=False)
    proxima_revision = Column(Date, nullable=False)
    fecha_registro = Column(Date, default=datetime.now, nullable=False)
    
    # Foreign key
    id_usuario = Column(Integer, ForeignKey("users.id_usuario"), nullable=False)
    
    # Relationships
    usuario = relationship("User", back_populates="maquinaria")
    mantenimientos = relationship("Mantenimiento", back_populates="equipo")
    
    def __repr__(self):
        return f"<Maquinaria {self.nombre_equipo}>"


# ============================================================================
# MANTENIMIENTO MODEL (Maintenance history)
# ============================================================================
class Mantenimiento(Base):
    __tablename__ = "mantenimientos"
    
    id_mantenimiento = Column(Integer, primary_key=True, index=True)
    id_equipo = Column(Integer, ForeignKey("maquinaria.id_equipo"), nullable=False)
    fecha_mantenimiento = Column(Date, default=datetime.now, nullable=False)
    tipo_mantenimiento = Column(String(100), nullable=False)  # preventivo, correctivo
    descripcion = Column(Text, nullable=False)
    costo = Column(Float, nullable=False)
    observaciones = Column(Text, nullable=True)
    
    # Relationships
    equipo = relationship("Maquinaria", back_populates="mantenimientos")
    
    def __repr__(self):
        return f"<Mantenimiento {self.id_equipo}>"


# ============================================================================
# CLIMA MODEL (Weather conditions)
# ============================================================================
class Clima(Base):
    __tablename__ = "clima"
    
    id_clima = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, default=datetime.now, nullable=False, index=True)
    temperatura = Column(Float, nullable=False)  # in Celsius
    humedad = Column(Float, nullable=False)  # percentage
    precipitacion = Column(Float, nullable=False)  # in mm
    viento = Column(Float, nullable=False)  # in km/h
    observaciones = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Clima {self.fecha}>"


# ============================================================================
# NÓMINA MODEL (Payroll / Employees)
# ============================================================================
class Nomina(Base):
    __tablename__ = "nomina"
    
    id_nomina = Column(Integer, primary_key=True, index=True)
    nombre_empleado = Column(String(150), nullable=False)
    cargo = Column(String(100), nullable=False)
    salario_base = Column(Float, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    estado = Column(String(20), default=OperationStatus.ACTIVE, nullable=False)
    documento = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Nomina {self.nombre_empleado}>"
