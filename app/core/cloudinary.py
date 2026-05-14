# app/core/cloudinary.py

import logging
from functools import lru_cache

import cloudinary
import cloudinary.uploader

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache
def configure_cloudinary() -> None:
    """
    Configure Cloudinary one time.
    """

    # Connect Cloudinary with app settings
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    # Log success message
    logger.info("Cloudinary configured successfully")


def get_cloudinary_uploader():
    """
    Return Cloudinary uploader.
    """

    # Make sure Cloudinary is configured
    configure_cloudinary()

    return cloudinary.uploader


def get_cloudinary_url_helper():
    """
    Return Cloudinary URL helper.
    """

    # Make sure Cloudinary is configured
    configure_cloudinary()

    from cloudinary.utils import cloudinary_url

    return cloudinary_url
