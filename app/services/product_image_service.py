# app/services/product_image_service.py
import logging
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database.models.product_image import ProductImage
from app.core.cloudinary import get_cloudinary_uploader

logger = logging.getLogger(__name__)


class ProductImageService:
    """Servicio para manejar imágenes de productos"""

    async def create_image_from_file(
        self,
        db: Session,
        product_id: int,
        image_file: UploadFile,
        is_main: bool = False,
    ) -> ProductImage:
        """
        Sube UNA imagen a un producto y la persiste en la DB.
        """

        # Validación
        if not image_file.content_type or not image_file.content_type.startswith(
            "image/"
        ):
            raise ValueError("El archivo no es una imagen válida")

        uploader = get_cloudinary_uploader()

        try:
            # Subida a Cloudinary (sync → threadpool) en otro hilo
            cloudinary_result = await run_in_threadpool(
                uploader.upload,
                image_file.file,
                folder="products",
            )

            # Garantizar imagen principal única
            if is_main:
                db.query(ProductImage).filter(
                    ProductImage.product_id == product_id,
                    ProductImage.is_main.is_(True),
                ).update({"is_main": False})

            product_image = ProductImage(
                url=cloudinary_result["secure_url"],
                cloud_id=cloudinary_result["public_id"],
                is_main=is_main,
                product_id=product_id,
            )

            db.add(product_image)
            db.commit()
            db.refresh(product_image)

            logger.info(
                "Imagen creada para producto %s: %s",
                product_id,
                cloudinary_result["public_id"],
            )

            return product_image

        except Exception:
            # 5️⃣ Rollback DB
            db.rollback()

            # 6️⃣ Limpieza Cloudinary si ya se subió
            if "cloudinary_result" in locals():
                await run_in_threadpool(
                    uploader.destroy,
                    cloudinary_result["public_id"],
                )

            logger.exception("Error creando imagen de producto")
            raise

    def get_image_by_id(self, db: Session, image_id: int) -> str | None:
        image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        return image.url if image else None

    def get_images_by_product(self, db: Session, product_id: int):
        return (
            db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        )
