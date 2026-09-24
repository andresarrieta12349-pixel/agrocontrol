"""
Crea el usuario administrador inicial (o convierte en admin a un usuario existente).

Uso, desde la carpeta del proyecto:
    docker compose exec backend python create_admin.py
"""
import getpass

from app.database import Base, SessionLocal, engine
from app import models
from app.auth import hash_password
from app.schemas import UsuarioRegister

Base.metadata.create_all(bind=engine)

datos = UsuarioRegister(
    nombre_completo=input("Nombre completo: "),
    nombre_usuario=input("Nombre de usuario (sin @): "),
    correo=input("Correo: "),
    password=getpass.getpass("Contraseña (mín. 8 caracteres): "),
)

db = SessionLocal()
try:
    if db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first():
        raise SystemExit("Ya existe un usuario con ese correo.")
    db.add(models.Usuario(
        nombre_completo=datos.nombre_completo,
        nombre_usuario=datos.nombre_usuario.lower(),
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        proveedor_auth=models.ProveedorAutenticacion.LOCAL,
        rol=models.RolUsuario.ADMIN,
    ))
    db.commit()
    print("Administrador creado.")
finally:
    db.close()