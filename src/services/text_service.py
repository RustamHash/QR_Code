"""
Сервис для обработки текстовых сообщений.
"""

from typing import List, Tuple

from ..core.exceptions import TextProcessingError, ValidationError, ValidationError
from ..core.logging_config import get_logger
from ..utils.validators import validate_text_length, validate_text_lines

logger = get_logger(__name__)


def process_text_message(text: str) -> Tuple[List[str], bool]:
    """
    Обрабатывает текстовое сообщение и определяет формат.

    Args:
        text: Текст сообщения

    Returns:
        Tuple[List[str], bool]: (список строк для QR-кодов, является ли одной строкой)

    Raises:
        TextProcessingError: если текст невалиден
    """
    try:
        # Валидируем длину текста
        validate_text_length(text)

        # Разбиваем на строки
        lines = validate_text_lines(text)

        # Определяем формат: одна строка или несколько
        is_single_line = len(lines) == 1

        logger.info(
            f"Текст обработан: {len(lines)} строк, "
            f"формат: {'одна строка' if is_single_line else 'несколько строк'}"
        )

        return lines, is_single_line

    except ValidationError as e:
        logger.error(f"Ошибка валидации текста: {e}")
        raise TextProcessingError(f"Текст не прошел валидацию: {e}") from e
    except Exception as e:
        logger.error(f"Ошибка при обработке текста: {e}", exc_info=True)
        if isinstance(e, TextProcessingError):
            raise
        raise TextProcessingError(f"Не удалось обработать текст: {e}") from e


def split_text_into_lines(text: str, max_lines: int = 1000) -> List[str]:
    """
    Разбивает текст на строки для обработки.

    Args:
        text: Текст для разбиения
        max_lines: Максимальное количество строк

    Returns:
        List[str]: Список непустых строк

    Raises:
        TextProcessingError: если количество строк превышает лимит
    """
    try:
        return validate_text_lines(text, max_lines=max_lines)
    except ValidationError as e:
        logger.error(f"Ошибка валидации при разбиении текста: {e}")
        raise TextProcessingError(f"Текст не прошел валидацию: {e}") from e
    except Exception as e:
        logger.error(f"Ошибка при разбиении текста на строки: {e}")
        if isinstance(e, TextProcessingError):
            raise
        raise TextProcessingError(f"Не удалось разбить текст на строки: {e}") from e
