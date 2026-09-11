from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password, verify_password
from app.repositories.user_repository import user_repository


class AuthService:
    def register(self, db: Session, payload: schemas.UsuarioRegister) -> models.Usuario:
        email = str(payload.correo).lower()
        if user_repository.get_by_email(db, email):
            raise ValueError("Ya existe un usuario registrado con ese correo")
        if user_repository.get_by_identifier(db, payload.nombre_usuario):
            raise ValueError("Ya existe un usuario con ese nombre de usuario")

        user = models.Usuario(
            nombre_completo=payload.nombre_completo.strip(),
            nombre_usuario=payload.nombre_usuario.strip().lower(),
            correo=email,
            telefono=payload.telefono,
            password_hash=hash_password(payload.password),
            rol=models.RolUsuario.OPERADOR,
            activo=True,
        )
        return user_repository.create(db, user)

    def authenticate(self, db: Session, identifier: str, password: str) -> Optional[models.Usuario]:
        user = user_repository.get_by_identifier(db, identifier)
        if not user or not user.activo or not verify_password(password, user.password_hash):
            return None
        return user

    def authenticate_google(self, db: Session, email: str, nombre_completo: Optional[str] = None) -> models.Usuario:
        email = email.lower().strip()
        user = user_repository.get_by_email(db, email)
        if user:
            if not user.activo:
                raise ValueError("El usuario asociado a esta cuenta de Google se encuentra inactivo")
            return user

        # Si el usuario no existe aún, lo creamos automáticamente con la cuenta de Google
        username_base = email.split("@")[0].replace(".", "_")
        username = username_base
        contador = 1
        while user_repository.get_by_identifier(db, username):
            username = f"{username_base}_{contador}"
            contador += 1

        nombre = nombre_completo.strip() if nombre_completo else email.split("@")[0].title()
        user = models.Usuario(
            nombre_completo=nombre,
            nombre_usuario=username,
            correo=email,
            password_hash=hash_password("GoogleAuth_OAuthPass_123!"),
            rol=models.RolUsuario.OPERADOR,
            activo=True,
        )
        return user_repository.create(db, user)


auth_service = AuthService()
