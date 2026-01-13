"""
Тесты для сервисов.
"""
import pytest
import io
from src.services.qr_service import generate_qr_code, generate_qr_codes
from src.services.excel_service import read_data_from_excel
from src.services.text_service import process_text_message
from src.core.exceptions import QRCodeGenerationError, TextProcessingError


def test_generate_qr_code():
    """Тест генерации одного QR-кода."""
    data = "test data"
    img = generate_qr_code(data)
    assert img is not None
    assert img.size[0] > 0
    assert img.size[1] > 0


def test_generate_qr_codes():
    """Тест генерации нескольких QR-кодов."""
    data_list = ["test1", "test2", "test3"]
    images = generate_qr_codes(data_list)
    assert len(images) == 3
    for img in images:
        assert img is not None


def test_process_text_single_line():
    """Тест обработки одной строки текста."""
    text = "single line"
    lines, is_single = process_text_message(text)
    assert len(lines) == 1
    assert is_single is True
    assert lines[0] == "single line"


def test_process_text_multiple_lines():
    """Тест обработки нескольких строк текста."""
    text = "line1\nline2\nline3"
    lines, is_single = process_text_message(text)
    assert len(lines) == 3
    assert is_single is False
    assert lines == ["line1", "line2", "line3"]


def test_process_text_empty():
    """Тест обработки пустого текста."""
    with pytest.raises(TextProcessingError):
        process_text_message("")


def test_process_text_only_spaces():
    """Тест обработки текста только с пробелами."""
    with pytest.raises(TextProcessingError):
        process_text_message("   \n  \n  ")

