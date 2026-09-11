from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> Optional[models.Usuario]:
        return db.query(models.Usuario).filter(models.Usuario.correo == email).first()

    def get_by_identifier(self, db: Session, identifier: str) -> Optional[models.Usuario]:
        normalized = identifier.strip().lower()
        return (
            db.query(models.Usuario)
            .filter(
                or_(
                    models.Usuario.nombre_usuario.ilike(normalized),
                    models.Usuario.correo.ilike(normalized),
                    models.Usuario.telefono == identifier.strip(),
                )
            )
            .first()
        )

    def get_by_id(self, db: Session, user_id: int) -> Optional[models.Usuario]:
        return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

    def create(self, db: Session, user: models.Usuario) -> models.Usuario:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()
