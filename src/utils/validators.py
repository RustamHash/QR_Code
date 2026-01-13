"""
Валидаторы для проверки данных.
"""
import re
from typing import List, Optional
from pathlib import Path

from ..core.exceptions import ValidationError
from ..core.config import get_settings
from ..core.logging_config import get_logger

logger = get_logger(__name__)


def validate_file_size(file_size: int) -> None:
    """
    Валидирует размер файла.
    
    Args:
        file_size: Размер файла в байтах
    
    Raises:
        ValidationError: если размер файла превышает лимит
    """
    settings = get_settings()
    max_size = settings.get_max_file_size_bytes()
    
    if file_size > max_size:
        max_mb = settings.max_file_size_mb
        raise ValidationError(
            f"Размер файла ({file_size / 1024 / 1024:.2f} MB) "
            f"превышает максимальный лимит ({max_mb} MB)"
        )


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> None:
    """
    Валидирует расширение файла.
    
    Args:
        filename: Имя файла
        allowed_extensions: Список разрешенных расширений (например, ['.xlsx', '.xls'])
    
    Raises:
        ValidationError: если расширение не разрешено
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    if extension not in allowed_extensions:
        raise ValidationError(
            f"Расширение файла '{extension}' не поддерживается. "
            f"Разрешенные расширения: {', '.join(allowed_extensions)}"
        )


def validate_text_length(text: str, max_length: Optional[int] = None) -> None:
    """
    Валидирует длину текста.
    
    Args:
        text: Текст для проверки
        max_length: Максимальная длина (если None, берется из настроек)
    
    Raises:
        ValidationError: если длина текста превышает лимит
    """
    if max_length is None:
        settings = get_settings()
        max_length = settings.max_text_length
    
    if len(text) > max_length:
        raise ValidationError(
            f"Длина текста ({len(text)} символов) "
            f"превышает максимальный лимит ({max_length} символов)"
        )


def validate_text_lines(text: str, max_lines: Optional[int] = None) -> List[str]:
    """
    Валидирует и разбивает текст на строки.
    
    Args:
        text: Текст для обработки
        max_lines: Максимальное количество строк (опционально)
    
    Returns:
        List[str]: Список непустых строк
    
    Raises:
        ValidationError: если количество строк превышает лимит
    """
    # Удаляем пустые строки и пробелы
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if max_lines and len(lines) > max_lines:
        raise ValidationError(
            f"Количество строк ({len(lines)}) "
            f"превышает максимальный лимит ({max_lines} строк)"
        )
    
    if not lines:
        raise ValidationError("Текст не содержит данных для обработки")
    
    return lines


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла от опасных символов.
    
    Args:
        filename: Исходное имя файла
    
    Returns:
        str: Очищенное имя файла
    """
    # Удаляем опасные символы
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Ограничиваем длину
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = Path(sanitized).stem, Path(sanitized).suffix
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized


def validate_pdf_settings(
    width: float,
    height: float,
    rows_per_page: int,
    columns_per_page: int
) -> None:
    """
    Валидирует настройки PDF.
    
    Args:
        width: Ширина страницы в мм
        height: Высота страницы в мм
        rows_per_page: Количество строк на странице
        columns_per_page: Количество колонок на странице
    
    Raises:
        ValidationError: если настройки невалидны
    """
    if width <= 0 or width > 1000:
        raise ValidationError("Ширина должна быть в диапазоне от 1 до 1000 мм")
    
    if height <= 0 or height > 1000:
        raise ValidationError("Высота должна быть в диапазоне от 1 до 1000 мм")
    
    if rows_per_page <= 0 or rows_per_page > 50:
        raise ValidationError("Количество строк на странице должно быть от 1 до 50")
    
    if columns_per_page <= 0 or columns_per_page > 10:
        raise ValidationError("Количество колонок на странице должно быть от 1 до 10")

