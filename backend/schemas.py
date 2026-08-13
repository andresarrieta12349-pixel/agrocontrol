"""
Pydantic Schemas for AgroControl Pro
Request/Response validation schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime
from typing import Optional, List


# ============================================================================
# AUTH SCHEMAS
# ============================================================================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    email: str
    rol: str
    fecha_registro: date
    estado: str
    
    class Config:
        from_attributes = True


# ============================================================================
# INSUMO SCHEMAS (Inputs/Inventory)
# ============================================================================
class InsumoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    tipo: str = Field(...)  # fertilizante, pesticida, fungicida, herbicida, semilla, otro
    cantidad: float = Field(..., gt=0)
    unidad: str = Field(...)  # kg, lt, u, bolsa, caneca
    precio: float = Field(..., gt=0)
    proveedor: str = Field(..., min_length=3)
    lote: Optional[str] = None
    fecha: date = Field(default_factory=date.today)
    
    @validator("tipo")
    def validate_tipo(cls, v):
        valid_tipos = ["fertilizante", "pesticida", "fungicida", "herbicida", "semilla", "otro"]
        if v not in valid_tipos:
            raise ValueError(f"Tipo debe ser uno de: {valid_tipos}")
        return v
    
    @validator("unidad")
    def validate_unidad(cls, v):
        valid_unidades = ["kg", "lt", "u", "bolsa", "caneca"]
        if v not in valid_unidades:
            raise ValueError(f"Unidad debe ser una de: {valid_unidades}")
        return v


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    precio: Optional[float] = None
    proveedor: Optional[str] = None
    lote: Optional[str] = None
    fecha: Optional[date] = None
    estado: Optional[str] = None


class InsumoResponse(InsumoBase):
    id_insumo: int
    total: float
    estado: str
    id_usuario: int
    
    class Config:
        from_attributes = True


class InsumoCountResponse(BaseModel):
    count: int


# ============================================================================
# GANADO SCHEMAS (Livestock/Animals)
# ============================================================================
class GanadoBase(BaseModel):
    id_animal_str: str = Field(..., max_length=50)
    nombre_animal: str = Field(..., min_length=3, max_length=150)
    tipo_animal: str = Field(...)  # bovino, porcino, ovino, caprino, equino, aviar
    raza: str = Field(..., min_length=2)
    sexo: str = Field(...)  # M o F
    edad: int = Field(..., ge=0, le=600)  # months
    peso: float = Field(..., gt=0)
    fecha_nacimiento: date = Field(...)
    estado_salud: str = Field(default="good")  # excellent, good, regular, sick
    valor_animal: float = Field(..., ge=0)
    
    @validator("tipo_animal")
    def validate_tipo(cls, v):
        valid_tipos = ["bovino", "porcino", "ovino", "caprino", "equino", "aviar"]
        if v not in valid_tipos:
            raise ValueError(f"Tipo debe ser uno de: {valid_tipos}")
        return v
    
    @validator("sexo")
    def validate_sexo(cls, v):
        if v.upper() not in ["M", "F"]:
            raise ValueError("Sexo debe ser 'M' o 'F'")
        return v.upper()
    
    @validator("estado_salud")
    def validate_salud(cls, v):
        valid_estados = ["excellent", "good", "regular", "sick"]
        if v not in valid_estados:
            raise ValueError(f"Estado debe ser uno de: {valid_estados}")
        return v


class GanadoCreate(GanadoBase):
    pass


class GanadoUpdate(BaseModel):
    nombre_animal: Optional[str] = None
    tipo_animal: Optional[str] = None
    raza: Optional[str] = None
    sexo: Optional[str] = None
    edad: Optional[int] = None
    peso: Optional[float] = None
    fecha_nacimiento: Optional[date] = None
    estado_salud: Optional[str] = None
    valor_animal: Optional[float] = None
    estado: Optional[str] = None


class GanadoResponse(GanadoBase):
    id_animal: int
    fecha_registro: date
    estado: str
    id_usuario: int
    
    class Config:
        from_attributes = True


class GanadoCountResponse(BaseModel):
    count: int


# ============================================================================
# MAQUINARIA SCHEMAS (Machinery/Equipment)
# ============================================================================
class MaquinariaBase(BaseModel):
    codigo_equipo: str = Field(..., max_length=100)
    nombre_equipo: str = Field(..., min_length=3, max_length=150)
    tipo_equipo: str = Field(...)  # tractor, cosechadora, arado, sembradora, pulverizador, rastrillo, otro
    marca: str = Field(..., min_length=2)
    modelo: str = Field(..., min_length=2)
    anno_fabricacion: int = Field(..., ge=1900)
    serie: Optional[str] = None
    estado: str = Field(default="bueno")  # excelente, bueno, regular, mantenimiento, inoperativo
    horas_trabajo: float = Field(default=0, ge=0)
    valor_adquisicion: float = Field(..., ge=0)
    fecha_adquisicion: date = Field(...)
    proxima_revision: date = Field(...)
    
    @validator("tipo_equipo")
    def validate_tipo(cls, v):
        valid_tipos = ["tractor", "cosechadora", "arado", "sembradora", "pulverizador", "rastrillo", "otro"]
        if v not in valid_tipos:
            raise ValueError(f"Tipo debe ser uno de: {valid_tipos}")
        return v
    
    @validator("estado")
    def validate_estado(cls, v):
        valid_estados = ["excelente", "bueno", "regular", "mantenimiento", "inoperativo"]
        if v not in valid_estados:
            raise ValueError(f"Estado debe ser uno de: {valid_estados}")
        return v


class MaquinariaCreate(MaquinariaBase):
    pass


class MaquinariaUpdate(BaseModel):
    nombre_equipo: Optional[str] = None
    tipo_equipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anno_fabricacion: Optional[int] = None
    serie: Optional[str] = None
    estado: Optional[str] = None
    horas_trabajo: Optional[float] = None
    valor_adquisicion: Optional[float] = None
    fecha_adquisicion: Optional[date] = None
    proxima_revision: Optional[date] = None


class MaquinariaResponse(MaquinariaBase):
    id_equipo: int
    fecha_registro: date
    id_usuario: int
    
    class Config:
        from_attributes = True


class MaquinariaCountResponse(BaseModel):
    count: int


# ============================================================================
# PESAJE SCHEMAS (Animal Weight)
# ============================================================================
class PesajeBase(BaseModel):
    id_animal: int
    peso: float = Field(..., gt=0)
    fecha_pesaje: date = Field(default_factory=date.today)
    observaciones: Optional[str] = None


class PesajeCreate(PesajeBase):
    pass


class PesajeResponse(PesajeBase):
    id_pesaje: int
    
    class Config:
        from_attributes = True


# ============================================================================
# MANTENIMIENTO SCHEMAS (Maintenance)
# ============================================================================
class MantenimientoBase(BaseModel):
    id_equipo: int
    tipo_mantenimiento: str  # preventivo, correctivo
    descripcion: str = Field(..., min_length=5)
    costo: float = Field(..., ge=0)
    observaciones: Optional[str] = None
    fecha_mantenimiento: date = Field(default_factory=date.today)


class MantenimientoCreate(MantenimientoBase):
    pass


class MantenimientoResponse(MantenimientoBase):
    id_mantenimiento: int
    
    class Config:
        from_attributes = True


# ============================================================================
# CLIMA SCHEMAS (Weather)
# ============================================================================
class ClimaBase(BaseModel):
    fecha: date = Field(default_factory=date.today)
    temperatura: float  # Celsius
    humedad: float = Field(..., ge=0, le=100)  # percentage
    precipitacion: float = Field(..., ge=0)  # mm
    viento: float = Field(..., ge=0)  # km/h
    observaciones: Optional[str] = None


class ClimaCreate(ClimaBase):
    pass


class ClimaResponse(ClimaBase):
    id_clima: int
    
    class Config:
        from_attributes = True


# ============================================================================
# NOMINA SCHEMAS (Payroll)
# ============================================================================
class NominaBase(BaseModel):
    nombre_empleado: str = Field(..., min_length=3)
    cargo: str = Field(..., min_length=3)
    salario_base: float = Field(..., gt=0)
    fecha_ingreso: date
    documento: Optional[str] = None


class NominaCreate(NominaBase):
    pass


class NominaUpdate(BaseModel):
    nombre_empleado: Optional[str] = None
    cargo: Optional[str] = None
    salario_base: Optional[float] = None
    fecha_ingreso: Optional[date] = None
    estado: Optional[str] = None
    documento: Optional[str] = None


class NominaResponse(NominaBase):
    id_nomina: int
    estado: str
    
    class Config:
        from_attributes = True
