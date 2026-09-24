"""
schemas.py
----------
Esquemas Pydantic v2 utilizados para validación de entrada/salida.

Toda entrada tiene límites de largo y de rango: sin ellos, un usuario (o un
atacante) podría enviar textos gigantes, números negativos, NaN o infinitos
que corrompen inventario/gastos o tumban el servidor.
"""
import re
from datetime import datetime, date
from typing import Annotated, Optional, List, Dict
from pydantic import (
    AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints,
    field_validator,
)

from app.models import (
    RolUsuario, ProveedorAutenticacion, TipoMovimiento, EstadoCiclo,
    SeveridadAlerta, CategoriaGasto,
)

# ---------------------------------------------------------------------------
# TIPOS REUTILIZABLES CON LÍMITES
# ---------------------------------------------------------------------------
Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
NombreCorto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Texto255 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
Texto50 = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
TextoLargo = Annotated[str, StringConstraints(max_length=2000)]
NoNegativo = Annotated[float, Field(ge=0, le=1e12, allow_inf_nan=False)]
Positivo = Annotated[float, Field(gt=0, le=1e12, allow_inf_nan=False)]
Horas = Annotated[float, Field(ge=0, le=24, allow_inf_nan=False)]
Telefono = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9+()\-\s]{5,30}$")]
# Sin "@" para que un nombre de usuario nunca pueda confundirse con un correo
# (el login acepta ambos en el mismo campo).
def _validar_nombre_usuario(valor: str) -> str:
    # Se valida en código (y no con una regex con "lookahead") porque el motor de
    # expresiones regulares de Pydantic v2 no soporta ese tipo de patrones.
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{3,100}", valor):
        raise ValueError("El nombre de usuario debe tener entre 3 y 100 caracteres: letras, números, punto, guion o guion bajo.")
    if not re.search(r"[A-Za-z]", valor):
        raise ValueError("El nombre de usuario debe incluir al menos una letra.")
    return valor


NombreUsuario = Annotated[
    str, StringConstraints(strip_whitespace=True), AfterValidator(_validar_nombre_usuario)
]

_CONTRASENAS_COMUNES = {
    "12345678", "123456789", "1234567890", "password", "password1", "contraseña",
    "qwertyui", "qwerty123", "11111111", "abc12345", "agrocontrol", "admin123",
}


def _validar_password(valor: str) -> str:
    # bcrypt sólo procesa los primeros 72 bytes: se rechaza en lugar de truncar en silencio.
    if len(valor.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar los 72 caracteres.")
    if valor.strip().lower() in _CONTRASENAS_COMUNES:
        raise ValueError("Esa contraseña es demasiado común. Elige una más difícil de adivinar.")
    return valor


Password = Annotated[str, Field(min_length=8, max_length=72), AfterValidator(_validar_password)]


# ---------------------------------------------------------------------------
# AUTENTICACIÓN
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    identificador: str = Field(
        ..., min_length=1, max_length=150,
        description="Correo, teléfono o nombre de usuario", examples=["operador@agrocontrolpro.com"],
    )
    # Sin regla de fortaleza: las cuentas existentes deben poder entrar.
    password: str = Field(..., min_length=1, max_length=128)


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
    nombre_completo: Nombre
    nombre_usuario: NombreUsuario
    telefono: Optional[Telefono] = None
    password: Password


class UsuarioRegister(BaseModel):
    nombre_completo: Nombre
    nombre_usuario: NombreUsuario
    correo: EmailStr
    telefono: Optional[Telefono] = None
    password: Password

    @field_validator("correo")
    @classmethod
    def _correo_en_minusculas(cls, valor):
        return valor.lower() if valor else valor


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[Nombre] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[Telefono] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None
    password: Optional[Password] = None


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
    nombre: Nombre
    ubicacion: Optional[Texto255] = None
    area_hectareas: NoNegativo = 0.0
    responsable: Optional[Nombre] = None


class FincaCreate(FincaBase):
    pass


class FincaUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    ubicacion: Optional[Texto255] = None
    area_hectareas: Optional[NoNegativo] = None
    responsable: Optional[Nombre] = None
    activo: Optional[bool] = None


class FincaOut(FincaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class LoteBase(BaseModel):
    finca_id: int
    nombre: NombreCorto
    area_hectareas: NoNegativo = 0.0
    tipo_cultivo: Optional[NombreCorto] = None


class LoteCreate(LoteBase):
    pass


class LoteUpdate(BaseModel):
    nombre: Optional[NombreCorto] = None
    area_hectareas: Optional[NoNegativo] = None
    tipo_cultivo: Optional[NombreCorto] = None
    activo: Optional[bool] = None


class LoteOut(LoteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool


class PotreroBase(BaseModel):
    lote_id: int
    nombre: NombreCorto
    capacidad_animales: int = Field(0, ge=0, le=100000)
    tipo_pasto: Optional[NombreCorto] = None


class PotreroCreate(PotreroBase):
    pass


class PotreroUpdate(BaseModel):
    lote_id: Optional[int] = None
    nombre: Optional[NombreCorto] = None
    capacidad_animales: Optional[int] = Field(None, ge=0, le=100000)
    tipo_pasto: Optional[NombreCorto] = None
    activo: Optional[bool] = None


class PotreroOut(PotreroBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class PastoBase(BaseModel):
    nombre: NombreCorto
    descripcion: Optional[Texto255] = None


class PastoCreate(PastoBase):
    pass


class PastoUpdate(BaseModel):
    nombre: Optional[NombreCorto] = None
    descripcion: Optional[Texto255] = None
    activo: Optional[bool] = None


class PastoOut(PastoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class AnimalBase(BaseModel):
    arete: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    peso_kg: Annotated[float, Field(gt=0, le=5000, allow_inf_nan=False)]
    estado_salud: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)] = "saludable"
    potrero_id: int


class AnimalCreate(AnimalBase):
    pass


class AnimalUpdate(BaseModel):
    arete: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]] = None
    peso_kg: Optional[Annotated[float, Field(gt=0, le=5000, allow_inf_nan=False)]] = None
    estado_salud: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)]] = None
    potrero_id: Optional[int] = None
    activo: Optional[bool] = None


class AnimalOut(AnimalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    creado_en: datetime


class ProveedorBase(BaseModel):
    nombre: Nombre
    nit: Optional[Texto50] = None
    contacto: Optional[Nombre] = None
    telefono: Optional[Texto50] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[Texto255] = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    nit: Optional[Texto50] = None
    contacto: Optional[Nombre] = None
    telefono: Optional[Texto50] = None
    correo: Optional[EmailStr] = None
    direccion: Optional[Texto255] = None
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
    nombre: Nombre
    ubicacion: Optional[Texto255] = None
    finca_id: Optional[int] = None


class BodegaCreate(BodegaBase):
    # La finca es obligatoria al crear: no se permite registrar una bodega
    # "huérfana" sin finca activa asociada (ver routers/inventory.py).
    finca_id: int


class BodegaUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    ubicacion: Optional[Texto255] = None
    finca_id: Optional[int] = None
    activo: Optional[bool] = None


class BodegaOut(BodegaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool


class ProductoBase(BaseModel):
    codigo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    nombre: Nombre
    categoria: Optional[NombreCorto] = None
    unidad_medida: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)] = "unidad"
    stock_minimo: NoNegativo = 0.0
    precio_unitario: NoNegativo = 0.0
    proveedor_id: Optional[int] = None


class ProductoCreate(ProductoBase):
    stock_actual: NoNegativo = 0.0


class ProductoUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    categoria: Optional[NombreCorto] = None
    unidad_medida: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]] = None
    stock_minimo: Optional[NoNegativo] = None
    precio_unitario: Optional[NoNegativo] = None
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
    cantidad: Positivo
    costo_unitario: NoNegativo = 0.0
    referencia: Optional[Texto255] = None
    observaciones: Optional[TextoLargo] = None


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
    nombre: Nombre
    cultivo: NombreCorto
    fecha_inicio: date
    fecha_estimada_cosecha: Optional[date] = None
    rendimiento_esperado_kg: NoNegativo = 0.0


class CicloProductivoCreate(CicloProductivoBase):
    pass


class CicloProductivoUpdate(BaseModel):
    nombre: Optional[Nombre] = None
    cultivo: Optional[NombreCorto] = None
    fecha_estimada_cosecha: Optional[date] = None
    fecha_fin_real: Optional[date] = None
    estado: Optional[EstadoCiclo] = None
    rendimiento_esperado_kg: Optional[NoNegativo] = None


class CicloProductivoOut(CicloProductivoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estado: EstadoCiclo
    fecha_fin_real: Optional[date] = None
    creado_en: datetime


class ActividadDiariaBase(BaseModel):
    ciclo_id: int
    fecha: date
    tipo_actividad: NombreCorto
    descripcion: Optional[TextoLargo] = None
    responsable: Optional[Nombre] = None
    horas_trabajo: Horas = 0.0
    insumos_utilizados: Optional[Texto255] = None


class ActividadDiariaCreate(ActividadDiariaBase):
    pass


class ActividadDiariaOut(ActividadDiariaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CosechaBase(BaseModel):
    ciclo_id: int
    fecha: date
    cantidad_kg: Positivo
    calidad: Optional[Texto50] = None
    observaciones: Optional[TextoLargo] = None


class CosechaCreate(CosechaBase):
    pass


class CosechaOut(CosechaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------------------------------------------------------------------------
# GASTOS
# ---------------------------------------------------------------------------
class GastoBase(BaseModel):
    categoria: CategoriaGasto
    descripcion: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    monto: Positivo
    fecha: date
    finca_id: Optional[int] = None


class GastoCreate(GastoBase):
    pass


class GastoUpdate(BaseModel):
    categoria: Optional[CategoriaGasto] = None
    descripcion: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]] = None
    monto: Optional[Positivo] = None
    fecha: Optional[date] = None
    finca_id: Optional[int] = None


class GastoOut(GastoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: Optional[int] = None
    creado_en: datetime


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
    gastos_por_categoria: Dict[str, float] = {}


TokenResponse.model_rebuild()