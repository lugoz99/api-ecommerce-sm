from fastapi import FastAPI

# Importa routers
from app.api.v1.endpoints import user  # apunta al user.py dentro de endpoints

app = FastAPI(
    title="Test Alembic App",
    description="API para probar Alembic y FastAPI con estructura en capas",
    version="1.0.0",
)

# Registrar routers
app.include_router(user.router)
