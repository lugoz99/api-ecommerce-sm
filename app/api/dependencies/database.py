# Funciones que FastAPI inyecta con Depends, reutilizables entre muchos endpoints.
"""
“¿Esto depende de FastAPI?”
Sí → api/dependencies/ o api/endpoints/
No → core/, services/, db/, etc.
"""
from app.database.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
