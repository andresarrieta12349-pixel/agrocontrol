from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories.product_repository import product_repository


class InventoryService:
    def list_products(self, db: Session, critical_only: bool = False) -> list[models.Producto]:
        products = product_repository.list_active(db)
        if critical_only:
            return [product for product in products if product.en_stock_critico]
        return products

    def create_product(self, db: Session, payload: schemas.ProductoCreate) -> models.Producto:
        if product_repository.get_by_code(db, payload.codigo):
            raise ValueError("Ya existe un producto con ese código")
        return product_repository.create(db, models.Producto(**payload.model_dump()))

    def update_product(
        self, db: Session, product_id: int, payload: schemas.ProductoUpdate
    ) -> models.Producto:
        product = product_repository.get(db, product_id)
        if not product:
            raise LookupError("Producto no encontrado")
        return product_repository.update(db, product, payload.model_dump(exclude_unset=True))

    def delete_product(self, db: Session, product_id: int) -> None:
        product = product_repository.get(db, product_id)
        if not product:
            raise LookupError("Producto no encontrado")
        product_repository.deactivate(db, product)


inventory_service = InventoryService()
