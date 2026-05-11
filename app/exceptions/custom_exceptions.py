"""
Excepciones personalizadas de la aplicación.

Estas excepciones se utilizan en toda la aplicación para manejar
diferentes casos de error de manera consistente.
"""


class ApplicationException(Exception):
    """Clase base para todas las excepciones de la aplicación."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(ApplicationException):
    """Se lanza cuando hay un error de validación de datos."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class NotFoundException(ApplicationException):
    """Se lanza cuando un recurso no es encontrado."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class UnauthorizedException(ApplicationException):
    """Se lanza cuando el usuario no está autenticado."""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, status_code=401)


class ForbiddenException(ApplicationException):
    """Se lanza cuando el usuario no tiene permisos suficientes."""
    
    def __init__(self, message: str = "Acceso prohibido"):
        super().__init__(message, status_code=403)


class ConflictException(ApplicationException):
    """Se lanza cuando hay un conflicto al crear o actualizar un recurso."""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class InternalServerException(ApplicationException):
    """Se lanza cuando hay un error interno del servidor."""
    
    def __init__(self, message: str = "Error interno del servidor"):
        super().__init__(message, status_code=500)
