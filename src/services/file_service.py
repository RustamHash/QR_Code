"""
Сервис для работы с файлами.
"""

import io
from typing import Optional
from pathlib import Path

from ..core.exceptions import FileProcessingError
from ..core.logging_config import get_logger
from ..utils.validators import validate_file_size, validate_file_extension, sanitize_filename
from ..utils.helpers import is_excel_file

logger = get_logger(__name__)


def validate_file(
    filename: str, file_data: bytes, allowed_extensions: Optional[list] = None
) -> None:
    """
    Валидирует файл.

    Args:
        filename: Имя файла
        file_data: Данные файла
        allowed_extensions: Список разрешенных расширений

    Raises:
        FileProcessingError: если файл невалиден
    """
    try:
        # Валидация размера
        validate_file_size(len(file_data))

        # Валидация расширения
        if allowed_extensions is None:
            allowed_extensions = [".xlsx", ".xls"]
        validate_file_extension(filename, allowed_extensions)

        logger.debug(f"Файл {filename} валидирован успешно")

    except Exception as e:
        logger.error(f"Ошибка валидации файла {filename}: {e}")
        if isinstance(e, FileProcessingError):
            raise
        raise FileProcessingError(f"Файл не прошел валидацию: {e}") from e


def read_file_to_bytesio(file_data: bytes) -> io.BytesIO:
    """
    Конвертирует байты файла в BytesIO.

    Args:
        file_data: Данные файла

    Returns:
        io.BytesIO: BytesIO объект
    """
    buffer = io.BytesIO(file_data)
    buffer.seek(0)
    return buffer


def get_safe_filename(filename: str) -> str:
    """
    Получает безопасное имя файла.

    Args:
        filename: Исходное имя файла

    Returns:
        str: Безопасное имя файла
    """
    return sanitize_filename(filename)


def is_valid_excel_file(filename: str) -> bool:
    """
    Проверяет, является ли файл валидным Excel файлом.

    Args:
        filename: Имя файла

    Returns:
        bool: True если файл Excel
    """
    return is_excel_file(filename)
