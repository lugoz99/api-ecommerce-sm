# app/routes/product_image.py

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

# DB
from app.database.session import get_db

# SERVICES
from app.schemas.product import ProductImageResponse
from app.services.product_image_service import ProductImageService

# SCHEMAS

router = APIRouter(
    prefix="/products",
    tags=["Product Images"],
)

# Instancia del servicio
product_image_service = ProductImageService()


@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    is_main: bool = Form(False),
    db: Session = Depends(get_db),
):
    """
    Endpoint para subir una imagen a un producto.

    Recibe:
    - product_id -> ID del producto
    - image -> archivo multipart/form-data
    - is_main -> indica si será la imagen principal

    Flujo:
    1. Recibe archivo
    2. Valida producto
    3. Sube a Cloudinary
    4. Guarda en DB
    5. Retorna metadata
    """

    product_image = await product_image_service.create_image_from_file(
        db=db,
        product_id=product_id,
        image_file=image,
        is_main=is_main,
    )

    return product_image
