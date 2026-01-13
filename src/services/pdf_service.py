"""
Сервис для создания PDF файлов с QR-кодами.
"""
import io
from typing import List, Optional, Union
from fpdf import FPDF
from qrcode.image.pil import PilImage

from ..core.exceptions import PDFGenerationError
from ..core.logging_config import get_logger
from .qr_service import generate_qr_codes, qr_image_to_bytes

logger = get_logger(__name__)


def create_qr_pdf(
    data_items: List[str],
    width: float = 75.0,
    height: float = 120.0,
    rows_per_page: int = 5,
    columns_per_page: int = 1,
    output_file: Optional[io.BytesIO] = None
) -> io.BytesIO:
    """
    Создает PDF файл с QR-кодами в виде сетки.
    
    Args:
        data_items: Список данных для QR-кодов
        width: Ширина страницы в мм
        height: Высота страницы в мм
        rows_per_page: Количество строк на странице
        columns_per_page: Количество колонок на странице
        output_file: BytesIO объект для вывода (если None, создается новый)
    
    Returns:
        io.BytesIO: BytesIO объект с PDF
    
    Raises:
        PDFGenerationError: если не удалось создать PDF
    """
    try:
        if not data_items:
            raise PDFGenerationError("Список данных пуст")
        
        # Генерируем QR-коды
        logger.info(f"Генерация {len(data_items)} QR-кодов...")
        qr_images = generate_qr_codes(data_items)
        
        # Создаем PDF
        pdf = FPDF(orientation='P', unit='mm', format=(width, height))
        
        # Отступы от краев страницы
        margin_x = 5
        margin_y = 5
        spacing = 5
        
        # Рассчитываем доступное пространство
        available_width = width - (2 * margin_x) - (spacing * (columns_per_page - 1))
        available_height = height - (2 * margin_y) - (spacing * (rows_per_page - 1))
        
        # Рассчитываем размер QR-кода (квадратный)
        qr_size_by_width = available_width / columns_per_page
        qr_size_by_height = available_height / rows_per_page
        qr_size = min(qr_size_by_width, qr_size_by_height)
        
        # Рассчитываем начальные позиции для центрирования сетки
        total_grid_width = (qr_size * columns_per_page) + (spacing * (columns_per_page - 1))
        total_grid_height = (qr_size * rows_per_page) + (spacing * (rows_per_page - 1))
        start_x = margin_x + (available_width - total_grid_width) / 2
        start_y = margin_y + (available_height - total_grid_height) / 2
        
        # Счетчики для позиционирования
        current_row = 0
        current_col = 0
        page_count = 0
        
        for i, qr_image in enumerate(qr_images, 1):
            # Если страница заполнена, создаем новую
            if current_row >= rows_per_page:
                pdf.add_page()
                current_row = 0
                current_col = 0
                page_count += 1
                logger.debug(f"Создана страница {page_count + 1}")
            
            # Рассчитываем позицию QR-кода
            x_pos = start_x + (current_col * (qr_size + spacing))
            y_pos = start_y + (current_row * (qr_size + spacing))
            
            # Конвертируем QR-код в байты
            img_bytes = qr_image_to_bytes(qr_image)
            
            # Сохраняем во временный файл для FPDF
            temp_file = io.BytesIO(img_bytes)
            
            # Добавляем QR-код на страницу
            pdf.image(temp_file, x=x_pos, y=y_pos, w=qr_size, h=qr_size)
            
            # Переходим к следующей позиции
            current_col += 1
            if current_col >= columns_per_page:
                current_col = 0
                current_row += 1
        
        # Создаем выходной буфер
        if output_file is None:
            output_file = io.BytesIO()
        
        # Сохраняем PDF в буфер
        pdf.output(output_file)
        output_file.seek(0)
        
        total_pages = page_count + 1
        logger.info(f"PDF файл создан: {len(data_items)} QR-кодов на {total_pages} страницах (сетка {rows_per_page}x{columns_per_page})")
        return output_file
        
    except PDFGenerationError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {e}", exc_info=True)
        raise PDFGenerationError(f"Не удалось создать PDF файл: {e}") from e

