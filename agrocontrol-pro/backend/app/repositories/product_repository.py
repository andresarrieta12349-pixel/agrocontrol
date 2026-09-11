from typing import Optional

from sqlalchemy.orm import Session

from app import models


class ProductRepository:
    def list_active(self, db: Session) -> list[models.Producto]:
        return (
            db.query(models.Producto)
            .filter(models.Producto.activo.is_(True))
            .order_by(models.Producto.nombre)
            .all()
        )

    def get(self, db: Session, product_id: int) -> Optional[models.Producto]:
        return db.query(models.Producto).filter(models.Producto.id == product_id).first()

    def get_by_code(self, db: Session, code: str) -> Optional[models.Producto]:
        return db.query(models.Producto).filter(models.Producto.codigo == code).first()

    def create(self, db: Session, product: models.Producto) -> models.Producto:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db: Session, product: models.Producto, values: dict) -> models.Producto:
        for field, value in values.items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
        return product

    def deactivate(self, db: Session, product: models.Producto) -> None:
        product.activo = False
        db.commit()


product_repository = ProductRepository()
