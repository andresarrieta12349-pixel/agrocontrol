"""
CRUD Operations for AgroControl Pro
Database operations for all entities
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import models
import schemas
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# AUTH CRUD
# ============================================================================
def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(models.User).filter(models.User.nombre_usuario == username).first()


def get_user(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id_usuario == user_id).first()


def create_user(db: Session, email: str, nombre_usuario: str, password: str, rol: str = "secretary"):
    """Create a new user"""
    db_user = models.User(
        email=email,
        nombre_usuario=nombre_usuario,
        password_hash=hash_password(password),
        rol=rol,
        estado="active"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============================================================================
# INSUMO CRUD (Inventory/Inputs)
# ============================================================================
def get_insumo(db: Session, insumo_id: int):
    """Get insumo by ID"""
    return db.query(models.Insumo).filter(models.Insumo.id_insumo == insumo_id).first()


def get_insumos(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    """Get all insumos with optional user filter"""
    query = db.query(models.Insumo)
    if user_id:
        query = query.filter(models.Insumo.id_usuario == user_id)
    return query.offset(skip).limit(limit).all()


def get_insumos_count(db: Session, user_id: int = None) -> int:
    """Get count of insumos"""
    query = db.query(func.count(models.Insumo.id_insumo))
    if user_id:
        query = query.filter(models.Insumo.id_usuario == user_id)
    return query.scalar()


def create_insumo(db: Session, insumo: schemas.InsumoCreate, user_id: int):
    """Create a new insumo"""
    total = insumo.cantidad * insumo.precio
    db_insumo = models.Insumo(
        nombre=insumo.nombre,
        tipo=insumo.tipo,
        cantidad=insumo.cantidad,
        unidad=insumo.unidad,
        precio=insumo.precio,
        fecha=insumo.fecha,
        proveedor=insumo.proveedor,
        lote=insumo.lote,
        total=total,
        estado="active",
        id_usuario=user_id
    )
    db.add(db_insumo)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo


def update_insumo(db: Session, insumo_id: int, insumo_update: schemas.InsumoUpdate):
    """Update an insumo"""
    db_insumo = get_insumo(db, insumo_id)
    if not db_insumo:
        return None
    
    update_data = insumo_update.dict(exclude_unset=True)
    
    # Recalculate total if cantidad or precio changed
    if "cantidad" in update_data or "precio" in update_data:
        cantidad = update_data.get("cantidad", db_insumo.cantidad)
        precio = update_data.get("precio", db_insumo.precio)
        update_data["total"] = cantidad * precio
    
    for field, value in update_data.items():
        setattr(db_insumo, field, value)
    
    db.commit()
    db.refresh(db_insumo)
    return db_insumo


def delete_insumo(db: Session, insumo_id: int):
    """Delete an insumo"""
    db_insumo = get_insumo(db, insumo_id)
    if db_insumo:
        db.delete(db_insumo)
        db.commit()
        return True
    return False


# ============================================================================
# GANADO CRUD (Livestock/Animals)
# ============================================================================
def get_ganado(db: Session, ganado_id: int):
    """Get animal by ID"""
    return db.query(models.Ganado).filter(models.Ganado.id_animal == ganado_id).first()


def get_ganado_by_id_str(db: Session, id_str: str):
    """Get animal by ID string"""
    return db.query(models.Ganado).filter(models.Ganado.id_animal_str == id_str).first()


def get_ganados(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    """Get all animals with optional user filter"""
    query = db.query(models.Ganado)
    if user_id:
        query = query.filter(models.Ganado.id_usuario == user_id)
    return query.offset(skip).limit(limit).all()


def get_ganados_count(db: Session, user_id: int = None) -> int:
    """Get count of animals"""
    query = db.query(func.count(models.Ganado.id_animal))
    if user_id:
        query = query.filter(models.Ganado.id_usuario == user_id)
    return query.scalar()


def create_ganado(db: Session, ganado: schemas.GanadoCreate, user_id: int):
    """Create a new animal"""
    # Check if ID already exists
    if get_ganado_by_id_str(db, ganado.id_animal_str):
        return None
    
    db_ganado = models.Ganado(
        id_animal_str=ganado.id_animal_str,
        nombre_animal=ganado.nombre_animal,
        tipo_animal=ganado.tipo_animal,
        raza=ganado.raza,
        sexo=ganado.sexo,
        edad=ganado.edad,
        peso=ganado.peso,
        fecha_nacimiento=ganado.fecha_nacimiento,
        estado_salud=ganado.estado_salud,
        valor_animal=ganado.valor_animal,
        estado="active",
        id_usuario=user_id
    )
    db.add(db_ganado)
    db.commit()
    db.refresh(db_ganado)
    return db_ganado


def update_ganado(db: Session, ganado_id: int, ganado_update: schemas.GanadoUpdate):
    """Update an animal"""
    db_ganado = get_ganado(db, ganado_id)
    if not db_ganado:
        return None
    
    update_data = ganado_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ganado, field, value)
    
    db.commit()
    db.refresh(db_ganado)
    return db_ganado


def delete_ganado(db: Session, ganado_id: int):
    """Delete an animal"""
    db_ganado = get_ganado(db, ganado_id)
    if db_ganado:
        db.delete(db_ganado)
        db.commit()
        return True
    return False


# ============================================================================
# MAQUINARIA CRUD (Machinery/Equipment)
# ============================================================================
def get_maquinaria(db: Session, maquinaria_id: int):
    """Get equipment by ID"""
    return db.query(models.Maquinaria).filter(models.Maquinaria.id_equipo == maquinaria_id).first()


def get_maquinaria_by_codigo(db: Session, codigo: str):
    """Get equipment by codigo"""
    return db.query(models.Maquinaria).filter(models.Maquinaria.codigo_equipo == codigo).first()


def get_maquinarias(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    """Get all equipment with optional user filter"""
    query = db.query(models.Maquinaria)
    if user_id:
        query = query.filter(models.Maquinaria.id_usuario == user_id)
    return query.offset(skip).limit(limit).all()


def get_maquinarias_count(db: Session, user_id: int = None) -> int:
    """Get count of equipment"""
    query = db.query(func.count(models.Maquinaria.id_equipo))
    if user_id:
        query = query.filter(models.Maquinaria.id_usuario == user_id)
    return query.scalar()


def create_maquinaria(db: Session, maquinaria: schemas.MaquinariaCreate, user_id: int):
    """Create new equipment"""
    # Check if codigo already exists
    if get_maquinaria_by_codigo(db, maquinaria.codigo_equipo):
        return None
    
    db_maquinaria = models.Maquinaria(
        codigo_equipo=maquinaria.codigo_equipo,
        nombre_equipo=maquinaria.nombre_equipo,
        tipo_equipo=maquinaria.tipo_equipo,
        marca=maquinaria.marca,
        modelo=maquinaria.modelo,
        anno_fabricacion=maquinaria.anno_fabricacion,
        serie=maquinaria.serie,
        estado=maquinaria.estado,
        horas_trabajo=maquinaria.horas_trabajo,
        valor_adquisicion=maquinaria.valor_adquisicion,
        fecha_adquisicion=maquinaria.fecha_adquisicion,
        proxima_revision=maquinaria.proxima_revision,
        id_usuario=user_id
    )
    db.add(db_maquinaria)
    db.commit()
    db.refresh(db_maquinaria)
    return db_maquinaria


def update_maquinaria(db: Session, maquinaria_id: int, maquinaria_update: schemas.MaquinariaUpdate):
    """Update equipment"""
    db_maquinaria = get_maquinaria(db, maquinaria_id)
    if not db_maquinaria:
        return None
    
    update_data = maquinaria_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_maquinaria, field, value)
    
    db.commit()
    db.refresh(db_maquinaria)
    return db_maquinaria


def delete_maquinaria(db: Session, maquinaria_id: int):
    """Delete equipment"""
    db_maquinaria = get_maquinaria(db, maquinaria_id)
    if db_maquinaria:
        db.delete(db_maquinaria)
        db.commit()
        return True
    return False


# ============================================================================
# PESAJE CRUD (Animal Weighing)
# ============================================================================
def create_pesaje(db: Session, pesaje: schemas.PesajeCreate):
    """Create a new weighing record"""
    db_pesaje = models.Pesaje(
        id_animal=pesaje.id_animal,
        peso=pesaje.peso,
        fecha_pesaje=pesaje.fecha_pesaje,
        observaciones=pesaje.observaciones
    )
    db.add(db_pesaje)
    db.commit()
    db.refresh(db_pesaje)
    return db_pesaje


def get_pesajes_by_animal(db: Session, animal_id: int):
    """Get all weighing records for an animal"""
    return db.query(models.Pesaje).filter(models.Pesaje.id_animal == animal_id).order_by(models.Pesaje.fecha_pesaje.desc()).all()


# ============================================================================
# MANTENIMIENTO CRUD (Equipment Maintenance)
# ============================================================================
def create_mantenimiento(db: Session, mantenimiento: schemas.MantenimientoCreate):
    """Create a new maintenance record"""
    db_mantenimiento = models.Mantenimiento(
        id_equipo=mantenimiento.id_equipo,
        fecha_mantenimiento=mantenimiento.fecha_mantenimiento,
        tipo_mantenimiento=mantenimiento.tipo_mantenimiento,
        descripcion=mantenimiento.descripcion,
        costo=mantenimiento.costo,
        observaciones=mantenimiento.observaciones
    )
    db.add(db_mantenimiento)
    db.commit()
    db.refresh(db_mantenimiento)
    return db_mantenimiento


def get_mantenimientos_by_equipo(db: Session, equipo_id: int):
    """Get all maintenance records for equipment"""
    return db.query(models.Mantenimiento).filter(models.Mantenimiento.id_equipo == equipo_id).order_by(models.Mantenimiento.fecha_mantenimiento.desc()).all()


# ============================================================================
# CLIMA CRUD (Weather)
# ============================================================================
def create_clima(db: Session, clima: schemas.ClimaCreate):
    """Create a new weather record"""
    db_clima = models.Clima(
        fecha=clima.fecha,
        temperatura=clima.temperatura,
        humedad=clima.humedad,
        precipitacion=clima.precipitacion,
        viento=clima.viento,
        observaciones=clima.observaciones
    )
    db.add(db_clima)
    db.commit()
    db.refresh(db_clima)
    return db_clima


def get_clima_by_fecha(db: Session, fecha: str):
    """Get weather record by date"""
    return db.query(models.Clima).filter(models.Clima.fecha == fecha).first()


def get_climas(db: Session, skip: int = 0, limit: int = 100):
    """Get all weather records"""
    return db.query(models.Clima).order_by(models.Clima.fecha.desc()).offset(skip).limit(limit).all()
