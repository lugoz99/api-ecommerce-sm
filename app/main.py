# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.cloudinary import configure_cloudinary

# Importar routers
from app.api.v1.endpoints import upload_product_image, user, product, category
from app.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan():
    """
    Maneja el ciclo de vida de la aplicación.
    - Código antes del yield: se ejecuta al INICIAR
    - Código después del yield: se ejecuta al CERRAR
    """
    # Startup
    configure_cloudinary()
    print("✅ Cloudinary configurado")
    print("🚀 Aplicación iniciada")

    yield  # Aquí la app está corriendo

    # Shutdown
    print("Aplicación cerrándose...")


app = FastAPI(
    title="Mi Tienda API",
    description="API para e-commerce con productos, categorías e imágenes",
    version="1.0.0",
    prefix="/api/v1",
    swagger_ui_parameters={
        # Todo cerrado al iniciar
        "docExpansion": "none",
        # Oculta el panel enorme de schemas
        "defaultModelsExpandDepth": -1,
        # Barra de búsqueda
        "filter": True,
        # Mantiene el token JWT aunque recargues
        "persistAuthorization": True,
        # Muestra tiempo del request
        "displayRequestDuration": True,
        # Dark theme para el código
        "syntaxHighlight.theme": "nord",
        # Habilita Try it out automáticamente
        "tryItOutEnabled": True,
        # Ordena tags
        "tagsSorter": "alpha",
        # Requests mejor renderizados
        "showExtensions": True,
        # Mejor lectura del JSON
        "defaultModelRendering": "model",
    },
)

# -------------------------------------------------------------------------------------------------------------------------
# Register routers
app.include_router(user.router, prefix="/users", tags=["Users"])

app.include_router(category.router, prefix="/categories", tags=["Categories"])

app.include_router(product.router, prefix="/products", tags=["Products"])

app.include_router(
    upload_product_image.router, prefix="/images", tags=["Product Images"]
)


"""
GET    /users              → Listar usuarios
GET    /users/{id}         → Un usuario (sin profile)
POST   /users              → Crear usuario
PUT    /users/{id}         → Actualizar usuario

GET    /users/{id}/profile           → Obtener profile
POST   /users/{id}/profile           → Crear profile
PUT    /users/{id}/profile           → Actualizar profile
DELETE /users/{id}/profile           → Eliminar profile

POST   /users/{id}/profile/image     → Subir imagen
DELETE /users/{id}/profile/image     → Eliminar imagen

"""

# -------------------------------------------------------------------------------------------------------------------------

register_exception_handlers(app)  # ← Registra los handlers


@app.get("/", tags=["System"])
def root():
    return {"message": "API funcionando"}


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
