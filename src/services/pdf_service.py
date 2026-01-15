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
    output_file: Optional[io.BytesIO] = None,
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
        pdf = FPDF(orientation="P", unit="mm", format=(width, height))

        # Отступы от краев страницы
        margin_x = 5
        top_margin = 10  # Отступ сверху
        bottom_margin = 5

        # Рассчитываем доступное пространство
        available_width = width - (2 * margin_x)
        available_height = height - top_margin - bottom_margin

        # Рассчитываем размер QR-кода (квадратный)
        # Для равномерного распределения используем весь доступный размер
        qr_size_by_width = (
            available_width / columns_per_page if columns_per_page > 0 else available_width
        )
        qr_size_by_height = (
            available_height / rows_per_page if rows_per_page > 0 else available_height
        )
        qr_size = min(qr_size_by_width, qr_size_by_height)

        # Равномерное распределение строк по вертикали
        # Используем весь доступный промежуток между top_margin и bottom_margin
        if rows_per_page > 1:
            # Равномерно распределяем строки с одинаковыми промежутками
            total_rows_height = qr_size * rows_per_page
            total_spacing_height = available_height - total_rows_height
            vertical_spacing = (
                total_spacing_height / (rows_per_page - 1) if rows_per_page > 1 else 0
            )
        else:
            vertical_spacing = 0

        # Распределение колонок по горизонтали
        column_positions = []
        if columns_per_page == 1:
            # 1 колонка - по центру
            column_positions = [margin_x + (available_width - qr_size) / 2]
        elif columns_per_page == 2:
            # 2 колонки - первая у левого края, вторая у правого края
            column_positions = [margin_x, width - margin_x - qr_size]
        else:
            # 3+ колонки - крайние у краев, остальные равномерно между ними
            total_columns_width = qr_size * columns_per_page
            total_horizontal_spacing = available_width - total_columns_width
            horizontal_spacing = (
                total_horizontal_spacing / (columns_per_page - 1) if columns_per_page > 1 else 0
            )

            # Первая колонка у левого края
            column_positions.append(margin_x)

            # Промежуточные колонки равномерно распределены
            for col in range(1, columns_per_page - 1):
                x_pos = margin_x + col * (qr_size + horizontal_spacing)
                column_positions.append(x_pos)

            # Последняя колонка у правого края
            column_positions.append(width - margin_x - qr_size)

        # Начальная позиция Y для первой строки
        start_y = top_margin

        # Счетчики для позиционирования
        current_row = 0
        current_col = 0
        page_count = 0

        # Создаем первую страницу
        pdf.add_page()
        page_count = 1
        logger.debug("Создана первая страница")

        for i, qr_image in enumerate(qr_images, 1):
            # Если текущая строка заполнена, создаем новую страницу
            if current_row >= rows_per_page:
                pdf.add_page()
                current_row = 0
                current_col = 0
                page_count += 1
                logger.debug(f"Создана страница {page_count}")

            # Рассчитываем позицию QR-кода
            # X позиция из предварительно рассчитанных позиций колонок
            x_pos = column_positions[current_col]

            # Y позиция - равномерное распределение строк
            if rows_per_page > 1:
                y_pos = start_y + current_row * (qr_size + vertical_spacing)
            else:
                # Если одна строка, центрируем по вертикали
                y_pos = top_margin + (available_height - qr_size) / 2

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

        total_pages = page_count
        logger.info(
            f"PDF файл создан: {len(data_items)} QR-кодов на {total_pages} страницах (сетка {rows_per_page}x{columns_per_page})"
        )
        return output_file

    except PDFGenerationError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании PDF: {e}", exc_info=True)
        raise PDFGenerationError(f"Не удалось создать PDF файл: {e}") from e
