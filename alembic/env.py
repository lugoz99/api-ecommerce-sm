import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# permitir importar app/
sys.path.append(str(Path(__file__).resolve().parents[1]))

# importar settings de tu core
from app.core.config import get_settings
from app.database.session import Base
from app.database import models  # fuerza carga de modelos


# cargar settings
settings = get_settings()

# Configuración de Alembic
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata de SQLAlchemy
target_metadata = Base.metadata

# Debug opcional
print("DEBUG - Tablas detectadas:", Base.metadata.tables)


# --------------------------------------------------
# Funciones para migraciones
# --------------------------------------------------
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
