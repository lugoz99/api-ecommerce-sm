"""

# 📁 Estructura del Proyecto

Este proyecto FastAPI sigue una arquitectura en capas pensada para:

- Mantener el código organizado
- Escalar bien en proyectos pequeños–medios
- Facilitar el mantenimiento y las pruebas
- Evitar sobreingeniería innecesaria

La estructura principal del proyecto es la siguiente:

```
project_name/
│
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── api/
│ │ ├── **init**.py
│ │ ├── v1/
│ │ │ ├── **init**.py
│ │ │ └── endpoints/
│ │ │ ├── user.py
│ │ │ ├── auth.py
│ │ │ └── item.py
│ │ └── dependencies/
│ │ ├── **init**.py
│ │ ├── database.py
│ │ └── auth.py
│ │
│ ├── core/
│ │ ├── **init**.py
│ │ ├── config.py
│ │ └── security.py
│ │
│ ├── database/
│ │ ├── **init**.py
│ │ ├── base.py
│ │ ├── session.py
│ │ └── models/
│ │ ├── **init**.py
│ │ ├── user.py
│ │ └── item.py
│ │
│ ├── schemas/
│ │ ├── **init**.py
│ │ ├── user.py
│ │ └── item.py
│ │
│ ├── services/
│ │ ├── **init**.py
│ │ ├── user_service.py
│ │ └── item_service.py
│ │
│ └── tests/
│ ├── **init**.py
│ ├── test_user.py
│ └── test_item.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## 🧩 Descripción de las carpetas

### app/main.py

Punto de entrada de la aplicación.

Aquí se crea la instancia de FastAPI y se registran los routers principales.
No debe contener lógica de negocio.

---

### app/api/

Capa de presentación (HTTP).  
Contiene todo lo relacionado con FastAPI.

#### api/v1/endpoints/

Aquí van los routers de FastAPI:

- Definición de endpoints
- Validación de entrada y salida usando schemas
- Llamadas a la capa de servicios

No debe contener:

- Lógica de negocio
- Acceso directo complejo a la base de datos

---

#### api/dependencies/

Aquí van las dependencias usadas con Depends:

- get_db() para sesión de base de datos
- get_current_user() para autenticación
- Dependencias de permisos o roles

Son funciones acopladas a FastAPI y reutilizables entre muchos endpoints.

---

### app/core/

Configuración y utilidades globales de la aplicación.

Aquí van:

- Carga de variables de entorno (Settings)
- Constantes globales
- Lógica transversal de seguridad:
  - Hashing de contraseñas
  - Creación y verificación de JWT

Regla importante:

Nada en core debe depender de FastAPI.

---

### app/db/

Capa de persistencia.

Aquí se define:

- Conexión a la base de datos (engine, SessionLocal)
- Base de SQLAlchemy
- Modelos ORM (tablas)

Responsabilidad:

- Infraestructura de base de datos
- Sin lógica de negocio

---

### app/schemas/

Modelos Pydantic para:

- Validar datos de entrada (requests)
- Definir datos de salida (responses)

Aquí no va:

- Lógica de negocio
- Acceso a base de datos

Solo definición de estructuras de datos.

---

### app/services/

Capa de lógica de negocio.

Aquí viven las reglas reales de la aplicación:

- Crear usuario
- Validar condiciones de negocio
- Orquestar operaciones entre modelos

No debe haber:

- APIRouter
- Depends
- Código específico de FastAPI

---

### app/tests/

Tests automatizados de la aplicación.

Se recomienda:

- Un archivo de test por módulo
- Probar servicios y endpoints críticos

---

## 🔄 Flujo típico de una petición

Request HTTP
↓
api/endpoints/ -> Router FastAPI
↓
schemas/ -> Validación de datos
↓
services/ -> Lógica de negocio
↓
db/models/ -> Persistencia
↓
Response

---

## 🎯 Principios de esta arquitectura

- Separación clara de responsabilidades
- La capa HTTP no contiene lógica de negocio
- La lógica de negocio no depende de FastAPI
- La infraestructura está aislada

Esta estructura permite:

- Escalar el proyecto con orden
- Facilitar el mantenimiento
- Testear cada capa de forma independiente
- Evolucionar la arquitectura sin reescribir todo
  """
  | Comando | Descripción |
  | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
  | `alembic init alembic` | Inicializa Alembic (solo una vez). Crea carpeta `alembic/` y `alembic.ini`. |
  | `alembic revision --autogenerate -m "mensaje"` | Crea un archivo de migración basado en los modelos de SQLAlchemy (`Base.metadata`). El `--autogenerate` detecta cambios automáticamente. |
  | `alembic upgrade head` | Aplica todas las migraciones pendientes hasta la última versión (`head`). |
  | `alembic downgrade -1` | Revierte la última migración aplicada. |
  | `alembic current` | Muestra la versión actual de la base de datos según Alembic. |
  | `alembic history` | Muestra el historial de migraciones aplicadas y pendientes. |
  | `alembic show <revision>` | Muestra los detalles de una migración específica. |

# Usando Uvicorn, desde la raíz del proyecto

2️⃣ Comandos para correr tu FastAPI
uvicorn app.main:app --reload

3️⃣ Acceder a Swagger

Una vez el servidor está corriendo:

Swagger UI: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

"""
interpretes = relationship('Interprete', cascade='all, delete, delete-orphan')
all ->se aplica para hacer propagación de operaciones cuando se guarda o actualiza información. Por ejemplo, cuando se crea una canción con dos intérpretes, al almacenar la canción se deben almacenar los intérpretes también.
delete -> se aplica al momento de borrar un objeto, de manera que los objetos relacionados también se borren. Por ejemplo, al borrar una canción se deben borrar sus intérpretes.
delete-orphan -> se aplica al momento de desasociar un objeto relacionado, por ejemplo, cuando un intérprete deja de hacer parte de una canción, al guardar los cambios el intérprete debe ser borrado
""""
