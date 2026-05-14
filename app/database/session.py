from sqlalchemy.engine import Engine, create_engine, URL
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import event
from datetime import datetime, timezone

from app.core.config import settings

DATABASE_URL = URL.create(
    drivername=settings.DB_DRIVER,
    username=settings.DB_USER,
    password=settings.DB_PASSWORD or None,  # maneja password vacío correctamente
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # verifica conexiones antes de usarlas | si sigue activa
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base para los modelos ORM
class Base(DeclarativeBase):
    pass


@event.listens_for(Base, "before_insert", propagate=True)
def receive_before_insert(mapper, connection, target):
    """Establece created_at y updated_at cuando se crea un registro"""

    now = datetime.now(timezone.utc)

    if hasattr(target, "created_at"):
        target.created_at = now

    if hasattr(target, "updated_at"):
        target.updated_at = now


@event.listens_for(Base, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """Actualiza updated_at cuando se modifica un registro"""

    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(timezone.utc)
