# app/services/product_image_service.py

import logging
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.cloudinary import get_cloudinary_uploader

# MODELOS
from app.database.models.product import Product
from app.database.models.product_image import ProductImage

# EXCEPCIONES PERSONALIZADAS
from app.exceptions.custom_exceptions import (
    ValidationException,
    NotFoundException,
)

logger = logging.getLogger(__name__)


class ProductImageService:
    """
    Servicio encargado de manejar las imágenes de productos.

    Responsabilidades:
    - Validar archivos
    - Subir imágenes a Cloudinary
    - Guardar metadata en DB
    - Garantizar imagen principal única
    - Manejar rollback y limpieza
    """

    async def create_image_from_file(
        self,
        db: Session,
        product_id: int,
        image_file: UploadFile,
        is_main: bool = False,
    ) -> ProductImage:
        """
        Sube una imagen a Cloudinary y la guarda en la base de datos.
        """

        # =========================================================
        # 1. VALIDAR QUE EL PRODUCTO EXISTA
        # =========================================================
        # Evita subir imágenes a productos inexistentes.
        product = db.get(Product, product_id)

        if not product:
            raise NotFoundException("Producto no encontrado")

        # =========================================================
        # 2. VALIDAR QUE EL ARCHIVO SEA UNA IMAGEN
        # =========================================================
        # content_type normalmente viene como:
        # image/png
        # image/jpeg
        # image/webp
        #
        # Si no empieza con "image/" rechazamos el archivo.
        if not image_file.content_type or not image_file.content_type.startswith(
            "image/"
        ):
            raise ValidationException("El archivo enviado no es una imagen válida")

        # =========================================================
        # 3. OBTENER CLIENTE DE CLOUDINARY
        # =========================================================
        uploader = get_cloudinary_uploader()

        try:

            # =====================================================
            # 4. SUBIR IMAGEN A CLOUDINARY
            # =====================================================
            #
            # Cloudinary SDK es síncrono.
            # Como FastAPI trabaja async, usamos:
            #
            # run_in_threadpool(...)
            #
            # para evitar bloquear el event loop.
            #
            # public_id:
            # Creamos un ID único para evitar colisiones.
            #
            # Ejemplo:
            # product_15_a8f91c3a...
            #
            cloudinary_result = await run_in_threadpool(
                uploader.upload,
                image_file.file,
                folder="products",
                public_id=f"product_{product_id}_{uuid.uuid4().hex}",
            )

            # =====================================================
            # 5. GARANTIZAR SOLO 1 IMAGEN PRINCIPAL
            # =====================================================
            #
            # Si la nueva imagen será principal:
            # - quitamos el flag is_main=True
            #   de las demás imágenes del producto.
            #
            if is_main:
                db.query(ProductImage).filter(
                    ProductImage.product_id == product_id,
                    ProductImage.is_main.is_(True),
                ).update({"is_main": False})

            # =====================================================
            # 6. CREAR REGISTRO EN DB
            # =====================================================
            #
            # secure_url:
            # URL HTTPS segura generada por Cloudinary.
            #
            # public_id:
            # ID interno para luego:
            # - eliminar
            # - transformar
            # - reemplazar
            #
            product_image = ProductImage(
                url=cloudinary_result["secure_url"],
                cloud_id=cloudinary_result["public_id"],
                is_main=is_main,
                product_id=product_id,
            )

            # ==================================git===================
            # 7. GUARDAR EN BASE DE DATOS
            # =====================================================
            db.add(product_image)

            # Persistir cambios
            db.commit()

            # Refrescar objeto desde DB
            db.refresh(product_image)

            # =====================================================
            # 8. LOG DE ÉXITO
            # =====================================================
            logger.info(
                "Imagen creada para producto %s: %s",
                product_id,
                cloudinary_result["public_id"],
            )

            return product_image

        except Exception:

            # =====================================================
            # 9. ROLLBACK SI ALGO FALLA
            # =====================================================
            db.rollback()

            # =====================================================
            # 10. LIMPIAR CLOUDINARY SI YA SE SUBIÓ
            # =====================================================
            #
            # Si la imagen ya fue subida
            # pero falló la DB,
            # eliminamos la imagen para evitar basura.
            #
            if "cloudinary_result" in locals():

                await run_in_threadpool(
                    uploader.destroy,
                    cloudinary_result["public_id"],
                )

            logger.exception("Error creando imagen de producto")

            # Re-lanzar excepción original
            raise

    def get_image_by_id(
        self,
        db: Session,
        image_id: int,
    ) -> ProductImage | None:
        """
        Obtiene una imagen por ID.

        Retorna el objeto completo,
        no solo la URL.
        """

        return db.query(ProductImage).filter(ProductImage.id == image_id).first()

    def get_images_by_product(
        self,
        db: Session,
        product_id: int,
    ) -> list[ProductImage]:
        """
        Obtiene todas las imágenes de un producto.
        """

        return (
            db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
        )
