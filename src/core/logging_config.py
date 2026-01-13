"""
Настройка логирования для приложения.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Настраивает логирование для приложения.
    
    Args:
        log_level: Уровень логирования (если None, берется из настроек)
        log_file: Путь к файлу логов (если None, берется из настроек)
        json_format: Использовать JSON формат для логов
    
    Returns:
        logging.Logger: настроенный логгер
    """
    settings = get_settings()
    
    level = log_level or settings.log_level
    log_file_path = log_file or settings.log_file
    
    # Создаем директорию для логов, если нужно
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Настраиваем формат
    if json_format:
        # Для JSON формата можно использовать structlog или python-json-logger
        # Пока используем простой формат
        log_format = '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    else:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настраиваем обработчики
    handlers = []
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # Файловый обработчик
    if log_file_path:
        file_handler = logging.FileHandler(
            log_file_path,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Настраиваем корневой логгер
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
        force=True
    )
    
    # Настраиваем логгеры для внешних библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено. Уровень: {level}, Файл: {log_file_path}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получает логгер с указанным именем.
    
    Args:
        name: Имя логгера (обычно __name__)
    
    Returns:
        logging.Logger: логгер
    """
    return logging.getLogger(name)

