# app/services/product_image_service.py

import logging
import uuid
import io

from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from PIL import Image

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
        # 2.1 VALIDAR CONTENIDO REAL CON PILLOW
        # =========================================================
        # Evita archivos falsificados que dicen ser imágenes
        # pero no lo son realmente.
        #
        try:
            # Leer contenido del archivo
            image_content = await image_file.read()

            # Validar que sea una imagen real
            img = Image.open(io.BytesIO(image_content))
            img.verify()

            # Resetear el cursor del archivo para poder leerlo después
            await image_file.seek(0)

        except Exception as e:
            logger.warning("Validación de imagen fallida: %s", str(e))
            raise ValidationException(
                "El archivo no es una imagen válida o está corrupto"
            )

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

    async def delete_product_image(
        self,
        db: Session,
        image_id: int,
    ) -> dict:
        """
        Elimina una imagen de un producto.

        Responsabilidades:
        - Buscar la imagen en BD
        - Eliminar de Cloudinary usando cloud_id
        - Eliminar registro de BD
        - Manejar errores

        Args:
            db: Sesión de base de datos
            image_id: ID de la imagen a eliminar

        Returns:
            dict con mensaje de éxito

        Raises:
            NotFoundException: Si la imagen no existe
        """

        # =====================================================
        # 1. BUSCAR IMAGEN EN BD
        # =====================================================
        image = db.query(ProductImage).filter(ProductImage.id == image_id).first()

        if not image:
            raise NotFoundException(f"Imagen con ID {image_id} no encontrada")

        # =====================================================
        # 2. OBTENER UPLOADER DE CLOUDINARY
        # =====================================================
        uploader = get_cloudinary_uploader()

        try:
            # =====================================================
            # 3. ELIMINAR DE CLOUDINARY USANDO cloud_id
            # =====================================================
            # El cloud_id es el public_id que guardamos al subir
            #
            # Ejemplo: product_15_a8f91c3a-1234
            #
            await run_in_threadpool(
                uploader.destroy,
                image.cloud_id,
            )

            # =====================================================
            # 4. ELIMINAR DE BASE DE DATOS
            # =====================================================
            db.delete(image)
            db.commit()

            # =====================================================
            # 5. LOG DE ÉXITO
            # =====================================================
            logger.info(
                "Imagen %s eliminada (cloud_id: %s)",
                image_id,
                image.cloud_id,
            )

            return {
                "success": True,
                "message": "Imagen eliminada correctamente",
                "image_id": image_id,
            }

        except Exception as e:
            db.rollback()
            logger.exception("Error eliminando imagen %s", image_id)
            raise

    async def replace_product_image(
        self,
        db: Session,
        image_id: int,
        image_file: UploadFile,
    ) -> ProductImage:
        """
        Reemplaza una imagen existente por una nueva.

        Flujo:
        1. Buscar imagen actual
        2. Validar nuevo archivo
        3. Subir a Cloudinary con MISMO cloud_id (overwrite=True)
        4. Actualizar URL en BD
        5. Si falla, restaurar imagen antigua

        Args:
            db: Sesión de base de datos
            image_id: ID de la imagen a reemplazar
            image_file: Nuevo archivo de imagen

        Returns:
            Objeto ProductImage actualizado

        Raises:
            NotFoundException: Si la imagen no existe
            ValidationException: Si el archivo no es válido
        """

        # =====================================================
        # 1. BUSCAR IMAGEN ACTUAL
        # =====================================================
        image = db.query(ProductImage).filter(ProductImage.id == image_id).first()

        if not image:
            raise NotFoundException(f"Imagen con ID {image_id} no encontrada")

        # =====================================================
        # 2. VALIDAR NUEVO ARCHIVO
        # =====================================================
        if not image_file.content_type or not image_file.content_type.startswith(
            "image/"
        ):
            raise ValidationException("El archivo enviado no es una imagen válida")

        try:
            image_content = await image_file.read()
            img = Image.open(io.BytesIO(image_content))
            img.verify()
            await image_file.seek(0)

        except Exception as e:
            logger.warning("Validación de imagen fallida: %s", str(e))
            raise ValidationException(
                "El archivo no es una imagen válida o está corrupto"
            )

        # =====================================================
        # 3. OBTENER UPLOADER
        # =====================================================
        uploader = get_cloudinary_uploader()

        try:
            # =====================================================
            # 4. SUBIR A CLOUDINARY CON MISMO cloud_id
            # =====================================================
            # overwrite=True permite reemplazar un archivo
            # existente si usamos el MISMO public_id
            #
            upload_result = await run_in_threadpool(
                uploader.upload,
                image_file.file,
                folder="products",
                public_id=image.cloud_id,  # ← MISMO ID (reemplaza)
                overwrite=True,
            )

            # =====================================================
            # 5. ACTUALIZAR URL EN BD
            # =====================================================
            # La URL puede cambiar si Cloudinary procesa la imagen
            # El cloud_id sigue siendo el mismo
            #
            image.url = upload_result["secure_url"]
            db.commit()
            db.refresh(image)

            # =====================================================
            # 6. LOG DE ÉXITO
            # =====================================================
            logger.info(
                "Imagen %s reemplazada (cloud_id: %s)",
                image_id,
                image.cloud_id,
            )

            return image

        except Exception as e:
            db.rollback()
            logger.exception("Error reemplazando imagen %s", image_id)
            raise

    def set_main_image(
        self,
        db: Session,
        product_id: int,
        image_id: int,
    ) -> ProductImage:
        """
        Establece una imagen como principal de un producto.

        Flujo:
        1. Quitar is_main=True de TODAS las imágenes del producto
        2. Establecer is_main=True en la imagen seleccionada
        3. Guardar cambios

        Args:
            db: Sesión de base de datos
            product_id: ID del producto
            image_id: ID de la imagen a establecer como principal

        Returns:
            Objeto ProductImage actualizado

        Raises:
            NotFoundException: Si la imagen no existe
        """

        # =====================================================
        # 1. BUSCAR IMAGEN
        # =====================================================
        image = (
            db.query(ProductImage)
            .filter(
                ProductImage.id == image_id,
                ProductImage.product_id == product_id,
            )
            .first()
        )

        if not image:
            raise NotFoundException(
                f"Imagen {image_id} no encontrada para el producto {product_id}"
            )

        try:
            # =====================================================
            # 2. QUITAR MAIN DE TODAS LAS IMÁGENES
            # =====================================================
            # Asegurar que solo haya UNA imagen principal
            #
            db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.is_main.is_(True),
            ).update({"is_main": False})

            # =====================================================
            # 3. ESTABLECER COMO PRINCIPAL LA NUEVA
            # =====================================================
            image.is_main = True
            db.commit()
            db.refresh(image)

            # =====================================================
            # 4. LOG DE ÉXITO
            # =====================================================
            logger.info(
                "Imagen %s establecida como principal para producto %s",
                image_id,
                product_id,
            )

            return image

        except Exception as e:
            db.rollback()
            logger.exception(
                "Error estableciendo imagen principal para producto %s",
                product_id,
            )
            raise
