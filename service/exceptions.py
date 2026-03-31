class CheckMindException(Exception):
    """Base application exception."""
    default_message = {
        'ru-RU': 'Что-то пошло не так',
        'en-EN': 'Something went wrong'
    }

    def __init__(self, message: dict = None, details: dict = None):
        if message:
            self.message = message
        else:
            self.message = self.default_message
        self.details = details or {}
        super().__init__(str(self.message))


class NotFoundError(CheckMindException):
    """Raised when a requested resource does not exist."""
    default_message = {
        'ru-RU': 'Ресурс не найден',
        'en-EN': 'Resource not found'
    }


class PermissionDeniedError(CheckMindException):
    """Raised when the user lacks permission to perform an action."""
    default_message = {
        'ru-RU': 'Доступ запрещён',
        'en-EN': 'Permission denied'
    }


class ValidationError(CheckMindException):
    """Raised when input data fails validation."""
    default_message = {
        'ru-RU': 'Ошибка валидации данных',
        'en-EN': 'Validation error'
    }


class ConflictError(CheckMindException):
    """Raised when an operation conflicts with the current state (business rule violation)."""
    default_message = {
        'ru-RU': 'Конфликт данных',
        'en-EN': 'Data conflict'
    }


class AuthenticationError(CheckMindException):
    """Raised when authentication fails (missing or invalid token)."""
    default_message = {
        'ru-RU': 'Ошибка аутентификации',
        'en-EN': 'Authentication error'
    }


class ExternalServiceError(CheckMindException):
    """Raised when an external service (VK, Google, email, etc.) fails."""
    default_message = {
        'ru-RU': 'Ошибка внешнего сервиса',
        'en-EN': 'External service error'
    }


class DatabaseError(CheckMindException):
    """Raised when a database operation fails (integrity, timeout, connection)."""
    default_message = {
        'ru-RU': 'Ошибка базы данных',
        'en-EN': 'Database error'
    }


class InternalServerError(CheckMindException):
    """Raised for unexpected internal errors not covered by other categories."""
    default_message = {
        'ru-RU': 'Внутренняя ошибка сервера',
        'en-EN': 'Internal server error'
    }