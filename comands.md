| Comando                                        | Descripción                                                                                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `alembic init alembic`                         | Inicializa Alembic (solo una vez). Crea carpeta `alembic/` y `alembic.ini`.                                                              |
| `alembic revision --autogenerate -m "mensaje"` | Crea un archivo de migración basado en los modelos de SQLAlchemy (`Base.metadata`). El `--autogenerate` detecta cambios automáticamente. |
| `alembic upgrade head`                         | Aplica todas las migraciones pendientes hasta la última versión (`head`).                                                                |
| `alembic downgrade -1`                         | Revierte la última migración aplicada.                                                                                                   |
| `alembic current`                              | Muestra la versión actual de la base de datos según Alembic.                                                                             |
| `alembic history`                              | Muestra el historial de migraciones aplicadas y pendientes.                                                                              |
| `alembic show <revision>`                      | Muestra los detalles de una migración específica.                                                                                        |

# Usando Uvicorn, desde la raíz del proyecto

2️⃣ Comandos para correr tu FastAPI
uvicorn app.main:app --reload

3️⃣ Acceder a Swagger

Una vez el servidor está corriendo:

Swagger UI: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc
