# app/core/cloudinary.py
import cloudinary
import cloudinary.uploader
from functools import lru_cache
import logging

from .config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def configure_cloudinary() -> None:
    """
    Configura Cloudinary una sola vez al iniciar la app.
    Usa @lru_cache para ejecutarse solo una vez.
    """
    settings = get_settings()

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=settings.CLOUDINARY_SECURE,
    )

    logger.info(f"Cloudinary configurado: {settings.CLOUDINARY_CLOUD_NAME}")


def get_cloudinary_uploader():
    """
    Obtiene el uploader de Cloudinary ya configurado.
    """
    configure_cloudinary()
    return cloudinary.uploader


def get_cloudinary_url_helper():
    """
    Obtiene helper para generar URLs de Cloudinary.
    """
    configure_cloudinary()
    from cloudinary.utils import cloudinary_url

    return cloudinary_url
