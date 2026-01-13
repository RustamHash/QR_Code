"""
Тесты для валидаторов.
"""
import pytest
from src.utils.validators import (
    validate_file_size,
    validate_file_extension,
    validate_text_length,
    validate_text_lines,
    sanitize_filename,
    validate_pdf_settings
)
from src.core.exceptions import ValidationError


def test_validate_file_size():
    """Тест валидации размера файла."""
    # Должно пройти для небольшого файла
    validate_file_size(1024 * 1024)  # 1 MB
    
    # Должно пройти для максимального размера
    validate_file_size(20 * 1024 * 1024)  # 20 MB
    
    # Должно вызвать ошибку для слишком большого файла
    with pytest.raises(ValidationError):
        validate_file_size(21 * 1024 * 1024)  # 21 MB


def test_validate_file_extension():
    """Тест валидации расширения файла."""
    validate_file_extension("test.xlsx", [".xlsx", ".xls"])
    validate_file_extension("test.XLSX", [".xlsx", ".xls"])  # Должно быть case-insensitive
    
    with pytest.raises(ValidationError):
        validate_file_extension("test.txt", [".xlsx", ".xls"])


def test_validate_text_length():
    """Тест валидации длины текста."""
    validate_text_length("short text", max_length=100)
    
    long_text = "a" * 1000
    validate_text_length(long_text, max_length=10000)
    
    with pytest.raises(ValidationError):
        validate_text_length("a" * 10001, max_length=10000)


def test_validate_text_lines():
    """Тест валидации и разбиения текста на строки."""
    lines = validate_text_lines("line1\nline2\nline3")
    assert len(lines) == 3
    assert lines == ["line1", "line2", "line3"]
    
    # Пустые строки должны быть удалены
    lines = validate_text_lines("line1\n\nline2\n  \nline3")
    assert len(lines) == 3
    
    with pytest.raises(ValidationError):
        validate_text_lines("")


def test_sanitize_filename():
    """Тест очистки имени файла."""
    assert sanitize_filename("test.xlsx") == "test.xlsx"
    assert sanitize_filename("test<>file.xlsx") == "test__file.xlsx"
    assert sanitize_filename("test/file.xlsx") == "test_file.xlsx"


def test_validate_pdf_settings():
    """Тест валидации настроек PDF."""
    validate_pdf_settings(75.0, 120.0, 5)
    
    with pytest.raises(ValidationError):
        validate_pdf_settings(-1, 120.0, 5)
    
    with pytest.raises(ValidationError):
        validate_pdf_settings(75.0, -1, 5)
    
    with pytest.raises(ValidationError):
        validate_pdf_settings(75.0, 120.0, 0)

