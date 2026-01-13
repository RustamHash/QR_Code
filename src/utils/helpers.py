"""
Вспомогательные функции.
"""
import io
from typing import Optional
from pathlib import Path


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в читаемый вид.
    
    Args:
        size_bytes: Размер в байтах
    
    Returns:
        str: Отформатированный размер
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_extension(filename: str) -> str:
    """
    Получает расширение файла.
    
    Args:
        filename: Имя файла
    
    Returns:
        str: Расширение файла (с точкой, в нижнем регистре)
    """
    return Path(filename).suffix.lower()


def is_excel_file(filename: str) -> bool:
    """
    Проверяет, является ли файл Excel файлом.
    
    Args:
        filename: Имя файла
    
    Returns:
        bool: True если файл Excel
    """
    extension = get_file_extension(filename)
    return extension in ['.xlsx', '.xls']


def create_bytes_io(data: bytes) -> io.BytesIO:
    """
    Создает BytesIO объект из байтов.
    
    Args:
        data: Данные в виде байтов
    
    Returns:
        io.BytesIO: BytesIO объект
    """
    buffer = io.BytesIO(data)
    buffer.seek(0)
    return buffer

