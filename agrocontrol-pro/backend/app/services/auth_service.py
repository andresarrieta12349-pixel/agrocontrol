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
        if not user or not user.activo or not user.password_hash:
            # Sin password_hash = cuenta creada por Google; no tiene login por contraseña.
            return None
        if not password or not verify_password(password, user.password_hash):
            return None
        return user

    def authenticate_google(
        self,
        db: Session,
        email: str,
        nombre_completo: Optional[str] = None,
        google_sub: Optional[str] = None,
    ) -> models.Usuario:
        """
        Autentica o crea un usuario a partir de una cuenta de Google ya
        verificada por el backend (correo con email_verified=True).

        - Nunca asigna una contraseña predeterminada ni simulada: los
          usuarios de Google se crean con password_hash=None, por lo que
          jamás podrán iniciar sesión por el formulario de correo/contraseña.
        - El rol siempre proviene de la base de datos: los usuarios nuevos
          se crean con el rol operativo mínimo (OPERADOR), nunca ADMIN.
        """
        email = email.lower().strip()

        # 1) Si ya conocemos este "sub" de Google, es la forma más confiable
        #    de reconocer al usuario (el correo de una cuenta puede cambiar).
        if google_sub:
            usuario_por_sub = (
                db.query(models.Usuario)
                .filter(models.Usuario.google_sub == google_sub)
                .first()
            )
            if usuario_por_sub:
                if not usuario_por_sub.activo:
                    raise ValueError("El usuario asociado a esta cuenta de Google se encuentra inactivo")
                return usuario_por_sub

        # 2) Si existe un usuario local con ese correo verificado, se vincula
        #    su cuenta a Google en vez de crear un usuario duplicado.
        user = user_repository.get_by_email(db, email)
        if user:
            if not user.activo:
                raise ValueError("El usuario asociado a esta cuenta de Google se encuentra inactivo")
            if google_sub and not user.google_sub:
                user.google_sub = google_sub
                user.proveedor_auth = models.ProveedorAutenticacion.GOOGLE
                db.commit()
                db.refresh(user)
            return user

        # 3) Usuario nuevo: se crea únicamente con lo que Google confirmó,
        #    sin contraseña ni rol de administrador.
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
            password_hash=None,
            proveedor_auth=models.ProveedorAutenticacion.GOOGLE,
            google_sub=google_sub,
            rol=models.RolUsuario.OPERADOR,
            activo=True,
        )
        return user_repository.create(db, user)


auth_service = AuthService()