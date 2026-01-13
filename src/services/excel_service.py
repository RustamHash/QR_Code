"""
Сервис для обработки Excel файлов.
"""
import io
from typing import List, Union
import pandas as pd

from ..core.exceptions import ExcelProcessingError
from ..core.logging_config import get_logger

logger = get_logger(__name__)


def read_data_from_excel(excel_file: Union[io.BytesIO, str], column_index: int = 0) -> List[str]:
    """
    Читает данные из Excel файла.
    
    Args:
        excel_file: Путь к файлу или BytesIO объект
        column_index: Индекс колонки для чтения (по умолчанию 0 - первая колонка)
    
    Returns:
        List[str]: Список данных из колонки
    
    Raises:
        ExcelProcessingError: если не удалось прочитать файл
    """
    try:
        # Читаем Excel файл
        df = pd.read_excel(excel_file, sheet_name=0, header=None)
        
        if df.empty:
            raise ExcelProcessingError("Excel файл пуст")
        
        # Получаем данные из указанной колонки
        if column_index >= len(df.columns):
            raise ExcelProcessingError(
                f"Колонка с индексом {column_index} не существует. "
                f"Доступно колонок: {len(df.columns)}"
            )
        
        column_data = df.iloc[:, column_index]
        
        # Удаляем пустые значения и конвертируем в список строк
        data_list = column_data.dropna().astype(str).tolist()
        
        # Фильтруем пустые строки
        data_list = [item.strip() for item in data_list if item.strip()]
        
        if not data_list:
            raise ExcelProcessingError("Не найдено данных в указанной колонке")
        
        logger.info(f"Прочитано {len(data_list)} записей из Excel файла")
        return data_list
        
    except pd.errors.EmptyDataError as e:
        logger.error(f"Excel файл пуст: {e}")
        raise ExcelProcessingError("Excel файл пуст или поврежден") from e
    except pd.errors.ExcelFileError as e:
        logger.error(f"Ошибка при чтении Excel файла: {e}")
        raise ExcelProcessingError(f"Не удалось прочитать Excel файл: {e}") from e
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке Excel файла: {e}", exc_info=True)
        raise ExcelProcessingError(f"Ошибка при обработке Excel файла: {e}") from e

