# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.cloudinary import configure_cloudinary

# Importar routers
from app.api.v1.endpoints import user, product, category
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
)


# Registrar routers
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])


app.include_router(category.router, prefix="/api/v1/categories", tags=["Categories"])
register_exception_handlers(app)  # ← Registra los handlers

@app.get("/")
def root():
    return {"message": "API funcionando"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
