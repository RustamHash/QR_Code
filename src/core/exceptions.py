"""
Кастомные исключения для приложения.
"""


class QRCodeBotException(Exception):
    """Базовое исключение для бота."""
    pass


class ConfigurationError(QRCodeBotException):
    """Ошибка конфигурации."""
    pass


class DatabaseError(QRCodeBotException):
    """Ошибка работы с базой данных."""
    pass


class FileProcessingError(QRCodeBotException):
    """Ошибка обработки файла."""
    pass


class ExcelProcessingError(FileProcessingError):
    """Ошибка обработки Excel файла."""
    pass


class TextProcessingError(QRCodeBotException):
    """Ошибка обработки текста."""
    pass


class ValidationError(QRCodeBotException):
    """Ошибка валидации данных."""
    pass


class QRCodeGenerationError(QRCodeBotException):
    """Ошибка генерации QR-кода."""
    pass


class PDFGenerationError(QRCodeBotException):
    """Ошибка генерации PDF."""
    pass


class RateLimitError(QRCodeBotException):
    """Превышен лимит запросов."""
    pass

