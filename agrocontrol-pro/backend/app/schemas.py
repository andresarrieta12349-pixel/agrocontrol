"""
schemas.py
----------
Esquemas Pydantic v2 utilizados para validación de entrada/salida.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.models import RolUsuario, ProveedorAutenticacion, TipoMovimiento, EstadoCiclo, SeveridadAlerta


# ---------------------------------------------------------------------------
# AUTENTICACIÓN
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    identificador: str = Field(
        ..., description="Correo, teléfono o nombre de usuario", examples=["operador@agrocontrolpro.com"]
    )
    password: str = Field(..., examples=["••••••••"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    usuario: "UsuarioOut"


class UsuarioBase(BaseModel):
    nombre_completo: str
    nombre_usuario: str
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    rol: RolUsuario = RolUsuario.OPERADOR


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=4)


class UsuarioRegister(BaseModel):
    nombre_completo: str = Field(..., min_length=2, max_length=150)
    nombre_usuario: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr
    telefono: Optional[str] = None
    password: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=4)


class UsuarioOut(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    proveedor_auth: ProveedorAutenticacion
    creado_en: datetime


# ---------------------------------------------------------------------------
# ADMINISTRACIÓN: FINCAS, LOTES, PROVEEDORES, POTREROS, PASTOS
# ---------------------------------------------------------------------------
class FincaBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None
    area_hectareas: float = 0.0
    responsable: Optional[str] = None


class FincaCreate(FincaBase):
    pass


class FincaUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    area_hectareas: Optional[float] = None
    responsable: Optional[str] = None
    activo: Optional[bool] = None


class FincaOut(FincaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class LoteBase(BaseModel):
    finca_id: int
    nombre: str
    area_hectareas: float = 0.0
    tipo_cultivo: Optional[str] = None


class LoteCreate(LoteBase):
    pass


class LoteUpdate(BaseModel):
    nombre: Optional[str] = None
    area_hectareas: Optional[float] = None
    tipo_cultivo: Optional[str] = None
    activo: Optional[bool] = None


class LoteOut(LoteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool


class PotreroBase(BaseModel):
    lote_id: int
    nombre: str = Field(..., min_length=1, max_length=100)
    capacidad_animales: int = Field(0, ge=0)
    tipo_pasto: Optional[str] = None


class PotreroCreate(PotreroBase):
    pass


class PotreroUpdate(BaseModel):
    lote_id: Optional[int] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    capacidad_animales: Optional[int] = Field(None, ge=0)
    tipo_pasto: Optional[str] = None
    activo: Optional[bool] = None


class PotreroOut(PotreroBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class PastoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None


class PastoCreate(PastoBase):
    pass


class PastoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class PastoOut(PastoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class AnimalBase(BaseModel):
    arete: str = Field(..., min_length=1, max_length=50)
    peso_kg: float = Field(..., gt=0)
    estado_salud: str = Field("saludable", min_length=2, max_length=50)
    potrero_id: int


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    arete: Optional[str] = Field(None, min_length=1, max_length=50)
    peso_kg: Optional[float] = Field(None, gt=0)
    estado_salud: Optional[str] = Field(None, min_length=2, max_length=50)
    potrero_id: Optional[int] = None
    activo: Optional[bool] = None


class AnimalOut(AnimalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class ProveedorBase(BaseModel):
    nombre: str
    nit: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class ProveedorOut(ProveedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


# ---------------------------------------------------------------------------
# INVENTARIO: BODEGAS, PRODUCTOS, MOVIMIENTOS
# ---------------------------------------------------------------------------
class BodegaBase(BaseModel):
    nombre: str
    ubicacion: Optional[str] = None
    finca_id: Optional[int] = None


class BodegaCreate(BodegaBase):
    # La finca es obligatoria al crear: no se permite registrar una bodega
    # "huérfana" sin finca activa asociada (ver routers/inventory.py).
    finca_id: int


class BodegaUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[str] = None
    finca_id: Optional[int] = None
    activo: Optional[bool] = None


class BodegaOut(BodegaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool


class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    categoria: Optional[str] = None
    unidad_medida: str = "unidad"
    stock_minimo: float = 0.0
    precio_unitario: float = 0.0
    proveedor_id: Optional[int] = None


class ProductoCreate(ProductoBase):
    stock_actual: float = 0.0


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[float] = None
    precio_unitario: Optional[float] = None
    proveedor_id: Optional[int] = None
    activo: Optional[bool] = None


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stock_actual: float
    activo: bool
    creado_en: datetime
    en_stock_critico: bool


class MovimientoInventarioBase(BaseModel):
    producto_id: int
    bodega_id: int
    tipo: TipoMovimiento
    cantidad: float = Field(..., gt=0)
    costo_unitario: float = 0.0
    referencia: Optional[str] = None
    observaciones: Optional[str] = None


class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass


class MovimientoInventarioOut(MovimientoInventarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: Optional[int] = None
    fecha: datetime


# ---------------------------------------------------------------------------
# PRODUCCIÓN AGRÍCOLA
# ---------------------------------------------------------------------------
class CicloProductivoBase(BaseModel):
    lote_id: int
    nombre: str
    cultivo: str
    fecha_inicio: date
    fecha_estimada_cosecha: Optional[date] = None
    rendimiento_esperado_kg: float = 0.0


class CicloProductivoCreate(CicloProductivoBase):
    pass


class CicloProductivoUpdate(BaseModel):
    nombre: Optional[str] = None
    cultivo: Optional[str] = None
    fecha_estimada_cosecha: Optional[date] = None
    fecha_fin_real: Optional[date] = None
    estado: Optional[EstadoCiclo] = None
    rendimiento_esperado_kg: Optional[float] = None


class CicloProductivoOut(CicloProductivoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estado: EstadoCiclo
    fecha_fin_real: Optional[date] = None
    creado_en: datetime


class ActividadDiariaBase(BaseModel):
    ciclo_id: int
    fecha: date
    tipo_actividad: str
    descripcion: Optional[str] = None
    responsable: Optional[str] = None
    horas_trabajo: float = 0.0
    insumos_utilizados: Optional[str] = None


class ActividadDiariaCreate(ActividadDiariaBase):
    pass


class ActividadDiariaOut(ActividadDiariaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CosechaBase(BaseModel):
    ciclo_id: int
    fecha: date
    cantidad_kg: float = Field(..., gt=0)
    calidad: Optional[str] = None
    observaciones: Optional[str] = None


class CosechaCreate(CosechaBase):
    pass


class CosechaOut(CosechaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------------------------------------------------------------------------
# ALERTAS Y DASHBOARD
# ---------------------------------------------------------------------------
class AlertaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    mensaje: str
    severidad: SeveridadAlerta
    modulo: Optional[str] = None
    resuelta: bool
    creado_en: datetime


class SerieSemanal(BaseModel):
    semana: str
    entradas: float
    salidas: float


class DashboardResumen(BaseModel):
    ciclos_activos: int
    ciclos_planificados: int
    alertas_criticas: int
    productos_stock_critico: int
    total_bodegas: int
    total_fincas: int
    valor_inventario: float
    movimientos_kardex_semanal: List[SerieSemanal]
    alertas_recientes: List[AlertaOut]


TokenResponse.model_rebuild()