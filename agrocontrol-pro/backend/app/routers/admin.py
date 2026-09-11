"""
routers/admin.py
------------------
Módulo de Administración: gestión de fincas, lotes, proveedores, usuarios,
potreros, animales y pastos.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, requerir_rol, hash_password

router = APIRouter(prefix="/api/admin", tags=["Administración"])


# ---------------------------------------------------------------------------
# FINCAS
# ---------------------------------------------------------------------------
@router.get("/fincas", response_model=List[schemas.FincaOut])
def listar_fincas(db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)):
    return (
        db.query(models.Finca)
        .filter(models.Finca.activo.is_(True))
        .order_by(models.Finca.nombre)
        .all()
    )


@router.post("/fincas", response_model=schemas.FincaOut, status_code=status.HTTP_201_CREATED)
def crear_finca(
    payload: schemas.FincaCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = models.Finca(**payload.model_dump())
    db.add(finca)
    db.commit()
    db.refresh(finca)
    return finca


@router.put("/fincas/{finca_id}", response_model=schemas.FincaOut)
def actualizar_finca(
    finca_id: int,
    payload: schemas.FincaUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = db.query(models.Finca).filter(models.Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(finca, campo, valor)
    db.commit()
    db.refresh(finca)
    return finca


@router.delete("/fincas/{finca_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_finca(
    finca_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    finca = db.query(models.Finca).filter(models.Finca.id == finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    finca.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# LOTES
# ---------------------------------------------------------------------------
@router.get("/lotes", response_model=List[schemas.LoteOut])
def listar_lotes(db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)):
    return (
        db.query(models.Lote)
        .filter(models.Lote.activo.is_(True))
        .order_by(models.Lote.nombre)
        .all()
    )


@router.post("/lotes", response_model=schemas.LoteOut, status_code=status.HTTP_201_CREATED)
def crear_lote(
    payload: schemas.LoteCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    finca = db.query(models.Finca).filter(models.Finca.id == payload.finca_id).first()
    if not finca:
        raise HTTPException(status_code=404, detail="Finca no encontrada")
    lote = models.Lote(**payload.model_dump())
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


@router.put("/lotes/{lote_id}", response_model=schemas.LoteOut)
def actualizar_lote(
    lote_id: int,
    payload: schemas.LoteUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    lote = db.query(models.Lote).filter(models.Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(lote, campo, valor)
    db.commit()
    db.refresh(lote)
    return lote


@router.delete("/lotes/{lote_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lote(
    lote_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    lote = db.query(models.Lote).filter(models.Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    lote.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# PROVEEDORES
# ---------------------------------------------------------------------------
@router.get("/proveedores", response_model=List[schemas.ProveedorOut])
def listar_proveedores(db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)):
    return (
        db.query(models.Proveedor)
        .filter(models.Proveedor.activo.is_(True))
        .order_by(models.Proveedor.nombre)
        .all()
    )


@router.post("/proveedores", response_model=schemas.ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    payload: schemas.ProveedorCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    proveedor = models.Proveedor(**payload.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.put("/proveedores/{proveedor_id}", response_model=schemas.ProveedorOut)
def actualizar_proveedor(
    proveedor_id: int,
    payload: schemas.ProveedorUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(proveedor, campo, valor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete("/proveedores/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(
    proveedor_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    proveedor.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# USUARIOS (solo administradores)
# ---------------------------------------------------------------------------
@router.get(
    "/usuarios",
    response_model=List[schemas.UsuarioOut],
    dependencies=[Depends(requerir_rol(models.RolUsuario.ADMIN))],
)
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).order_by(models.Usuario.nombre_completo).all()


@router.post(
    "/usuarios",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_rol(models.RolUsuario.ADMIN))],
)
def crear_usuario(payload: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(models.Usuario)
        .filter(models.Usuario.nombre_usuario == payload.nombre_usuario)
        .first()
    )
    if existente:
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está en uso")

    usuario = models.Usuario(
        nombre_completo=payload.nombre_completo,
        nombre_usuario=payload.nombre_usuario,
        correo=payload.correo,
        telefono=payload.telefono,
        rol=payload.rol,
        password_hash=hash_password(payload.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put(
    "/usuarios/{usuario_id}",
    response_model=schemas.UsuarioOut,
    dependencies=[Depends(requerir_rol(models.RolUsuario.ADMIN))],
)
def actualizar_usuario(usuario_id: int, payload: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos = payload.model_dump(exclude_unset=True)
    if "password" in datos and datos["password"]:
        usuario.password_hash = hash_password(datos.pop("password"))
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete(
    "/usuarios/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(requerir_rol(models.RolUsuario.ADMIN))],
)
def desactivar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# POTREROS
# ---------------------------------------------------------------------------
@router.get("/potreros", response_model=List[schemas.PotreroOut])
def listar_potreros(db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)):
    return (
        db.query(models.Potrero)
        .filter(models.Potrero.activo.is_(True))
        .order_by(models.Potrero.nombre)
        .all()
    )


@router.post("/potreros", response_model=schemas.PotreroOut, status_code=status.HTTP_201_CREATED)
def crear_potrero(
    payload: schemas.PotreroCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    lote = db.query(models.Lote).filter(models.Lote.id == payload.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    potrero = models.Potrero(**payload.model_dump())
    db.add(potrero)
    db.commit()
    db.refresh(potrero)
    return potrero


@router.put("/potreros/{potrero_id}", response_model=schemas.PotreroOut)
def actualizar_potrero(
    potrero_id: int,
    payload: schemas.PotreroUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    potrero = db.query(models.Potrero).filter(models.Potrero.id == potrero_id).first()
    if not potrero:
        raise HTTPException(status_code=404, detail="Potrero no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(potrero, campo, valor)
    db.commit()
    db.refresh(potrero)
    return potrero


@router.delete("/potreros/{potrero_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_potrero(
    potrero_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    potrero = db.query(models.Potrero).filter(models.Potrero.id == potrero_id).first()
    if not potrero:
        raise HTTPException(status_code=404, detail="Potrero no encontrado")
    potrero.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# ANIMALES
# ---------------------------------------------------------------------------
@router.get("/animales", response_model=List[schemas.AnimalOut])
def listar_animales(db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)):
    return (
        db.query(models.Animal)
        .filter(models.Animal.activo.is_(True))
        .order_by(models.Animal.arete)
        .all()
    )


@router.post("/animales", response_model=schemas.AnimalOut, status_code=status.HTTP_201_CREATED)
def crear_animal(
    payload: schemas.AnimalCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    potrero = db.query(models.Potrero).filter(models.Potrero.id == payload.potrero_id).first()
    if not potrero:
        raise HTTPException(status_code=404, detail="Potrero no encontrado")
    existente = db.query(models.Animal).filter(models.Animal.arete == payload.arete).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un animal con ese código/arete")
    animal = models.Animal(**payload.model_dump())
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


@router.put("/animales/{animal_id}", response_model=schemas.AnimalOut)
def actualizar_animal(
    animal_id: int,
    payload: schemas.AnimalUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(animal, campo, valor)
    db.commit()
    db.refresh(animal)
    return animal


@router.delete("/animales/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_animal(
    animal_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    animal.activo = False
    db.commit()
    return None


# ---------------------------------------------------------------------------
# PASTOS (GESTIÓN DE PASTOS Y FORRAJES)
# ---------------------------------------------------------------------------
@router.get("/pastos", response_model=List[schemas.PastoOut])
def listar_pastos(
    incluir_inactivos: bool = True,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    query = db.query(models.Pasto)
    if not incluir_inactivos:
        query = query.filter(models.Pasto.activo.is_(True))
    pastos = query.order_by(models.Pasto.nombre).all()
    if not pastos:
        pastos_defecto = [
            models.Pasto(nombre="Brachiaria decumbens", descripcion="Pasto tropical de excelente cobertura"),
            models.Pasto(nombre="Kikuyo (Cenchrus clandestinus)", descripcion="Resistente al pastoreo en clima frío/medio"),
            models.Pasto(nombre="Pasto Caimán", descripcion="Tolerante a suelos húmedos e inundables"),
            models.Pasto(nombre="Mombaça (Panicum maximum)", descripcion="Alto rendimiento en biomasa y nutrientes"),
            models.Pasto(nombre="Pasto Estrella (Cynodon nlemfuensis)", descripcion="Crecimiento rápido estolonífero"),
            models.Pasto(nombre="Pangola (Digitaria eriantha)", descripcion="Excelente palatabilidad para el ganado")
        ]
        db.add_all(pastos_defecto)
        db.commit()
        pastos = db.query(models.Pasto).order_by(models.Pasto.nombre).all()
    return pastos


@router.post("/pastos", response_model=schemas.PastoOut, status_code=status.HTTP_201_CREATED)
def crear_pasto(
    payload: schemas.PastoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    existente = db.query(models.Pasto).filter(models.Pasto.nombre == payload.nombre).first()
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un pasto con ese nombre")
    pasto = models.Pasto(**payload.model_dump())
    db.add(pasto)
    db.commit()
    db.refresh(pasto)
    return pasto


@router.put("/pastos/{pasto_id}", response_model=schemas.PastoOut)
def actualizar_pasto(
    pasto_id: int,
    payload: schemas.PastoUpdate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
    pasto = db.query(models.Pasto).filter(models.Pasto.id == pasto_id).first()
    if not pasto:
        raise HTTPException(status_code=404, detail="Pasto no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(pasto, campo, valor)
    db.commit()
    db.refresh(pasto)
    return pasto


@router.delete("/pastos/{pasto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pasto(
    pasto_id: int, db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
    pasto = db.query(models.Pasto).filter(models.Pasto.id == pasto_id).first()
    if not pasto:
        raise HTTPException(status_code=404, detail="Pasto no encontrado")
    pasto.activo = False
    db.commit()
    return None