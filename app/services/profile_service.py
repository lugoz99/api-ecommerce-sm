import io
import uuid

from exceptiongroup import catch
from fastapi import UploadFile
from fastapi.exceptions import ValidationException
from pymysql import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cloudinary import get_cloudinary_uploader
from app.database.models.profile import Profile
from app.exceptions.custom_exceptions import (
    NotFoundException,
    InternalServerException,
)
from app.schemas.profile import ProfileCreate
import logging
from PIL import Image
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


class ProfileService:

    @staticmethod
    def create(db: Session, profile_data: ProfileCreate):
        new_profile = Profile(**profile_data.model_dump())
        try:
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        except IntegrityError as e:
            logger.error("DATABASE ERRROR", e)

    @staticmethod
    async def upload_profile_image(db: Session, user_id: int, image_file: UploadFile):
        """
        Sube o actualiza la imagen de perfil de un usuario.

        Flujo:
        1. Validar archivo (content_type + Pillow)
        2. Buscar profile del usuario
        3. Subir a Cloudinary con overwrite=True
           (primera vez: crea, actualizaciones: reemplaza)
        4. Guardar URL + cloud_id en BD
        5. Si falla: rollback + limpiar Cloudinary

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            image_file: Archivo de imagen

        Returns:
            Objeto Profile actualizado

        Raises:
            ValidationException: Si el archivo no es válido
            NotFoundException: Si no existe profile para el usuario
            InternalServerException: Si hay error en la subida
        """
        try:
            # =====================================================
            # 1. VALIDAR content_type
            # =====================================================
            if not image_file.content_type or not image_file.content_type.startswith(
                "image/"
            ):
                raise ValidationException("El archivo enviado no es una imagen válida")

            # =====================================================
            # 2. VALIDAR CONTENIDO CON PILLOW
            # =====================================================
            photo_content = await image_file.read()

            # Validar que sea una imagen real (no falsificada)
            await run_in_threadpool(
                lambda: Image.open(io.BytesIO(photo_content)).verify()
            )

            # Resetear cursor para lectura posterior
            await image_file.seek(0)

            # =====================================================
            # 3. BUSCAR PROFILE DEL USUARIO
            # =====================================================
            profile_db = db.execute(
                select(Profile).where(Profile.user_id == user_id)
            ).scalar_one_or_none()

            if not profile_db:
                raise NotFoundException(f"Profile no existe para el usuario {user_id}")

            # =====================================================
            # 4. OBTENER UPLOADER
            # =====================================================
            uploader = get_cloudinary_uploader()

            # =====================================================
            # 5. SUBIR A CLOUDINARY CON overwrite=True
            # =====================================================
            # public_id fijo por usuario:
            # - Primera carga: CREA la imagen
            # - Actualizaciones: REEMPLAZA la imagen anterior
            #
            # Ventajas:
            # - Solo 1 imagen por usuario en Cloudinary
            # - No se acumula basura
            # - URL se mantiene igual (solo cambia el contenido)
            #
            upload_result = await run_in_threadpool(
                uploader.upload,
                image_file.file,
                folder="profile_images",
                public_id=f"profile_{user_id}",  # ← Fijo, no UUID
                overwrite=True,  # ← Reemplaza si existe
            )

            # =====================================================
            # 6. GUARDAR EN BASE DE DATOS
            # =====================================================
            profile_db.url_photo = upload_result.get("secure_url")
            profile_db.cloud_id = upload_result.get("public_id")
            db.commit()
            db.refresh(profile_db)

            # =====================================================
            # 7. LOG DE ÉXITO
            # =====================================================
            logger.info(
                "Imagen de perfil subida/actualizada para usuario %s (cloud_id: %s)",
                user_id,
                profile_db.cloud_id,
            )

            return {
                "url_photo": profile_db.url_photo,
                "cloud_id": profile_db.cloud_id,
                "message": "Imagen actualizada correctamente"
            }

        except (ValidationException, NotFoundException):
            # Excepciones conocidas: se re-lanzan sin modificar
            raise
        except Exception as e:
            # Excepciones inesperadas: rollback + limpiar Cloudinary
            db.rollback()

            if "upload_result" in locals():
                # La imagen SÍ se subió a Cloudinary pero falló algo después
                # Eliminar para evitar basura
                try:
                    await run_in_threadpool(
                        uploader.destroy, upload_result["public_id"]
                    )
                    logger.info(
                        "Imagen de Cloudinary limpiada después de error: %s",
                        upload_result["public_id"],
                    )
                except Exception as cleanup_error:
                    logger.warning(
                        "Fallo al limpiar imagen de Cloudinary: %s", cleanup_error
                    )

            logger.exception("Error subiendo imagen de perfil para usuario %s", user_id)
            raise InternalServerException("Error al subir la imagen del perfil")

    @staticmethod
    def get(db: Session):
        return db.scalars(select(Profile)).all()

    @staticmethod
    def update(db: Session, id: int, profile_data: ProfileCreate):
        profile_db = db.get(Profile, id)
        if not profile_db:
            raise ValueError("Profile doesn't exits")

        update_profile = profile_data.model_dump(exclude_unset=True)
        for key, value in update_profile.items():
            setattr(profile_db, key, value)
        try:
            db.commit()
            db.refresh(profile_db)
            return profile_db
        except IntegrityError as e:
            logger.error("DATABASE ERRROR", e)
