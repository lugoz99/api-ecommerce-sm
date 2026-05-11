"""
Manejadores de excepciones para FastAPI.

Registra los manejadores de excepciones personalizadas
para convertirlas en respuestas HTTP apropiadas.
"""

from fastapi import FastAPI
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from .custom_exceptions import ApplicationException
from fastapi import Request
from datetime import datetime


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra los manejadores de excepciones en la aplicación FastAPI.

    Args:
        app: Instancia de la aplicación FastAPI
    """

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": str(exc.message),
                    "type": exc.__class__.__name__,
                    "status_code": exc.status_code,
                },
                "path": request.url.path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
