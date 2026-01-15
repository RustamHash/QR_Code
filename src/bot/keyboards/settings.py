"""
Клавиатуры для настроек.
"""

from typing import Dict, Union
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_settings_keyboard(settings: Dict[str, float | int]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с настройками.

    Args:
        settings: Словарь с настройками (width, height, rows_per_page, columns_per_page)

    Returns:
        InlineKeyboardMarkup: Клавиатура с настройками
    """
    width = settings.get("width", 75)
    height = settings.get("height", 120)
    rows_per_page = settings.get("rows_per_page", 5)
    columns_per_page = settings.get("columns_per_page", 1)

    keyboard = [
        [
            InlineKeyboardButton(f"📏 Ширина: {width}", callback_data="menu_width"),
            InlineKeyboardButton(f"📐 Высота: {height}", callback_data="menu_height"),
        ],
        [
            InlineKeyboardButton(f"📊 Строки: {rows_per_page}", callback_data="menu_rows"),
            InlineKeyboardButton(f"📋 Колонки: {columns_per_page}", callback_data="menu_columns"),
        ],
        [
            InlineKeyboardButton("🔄 Сбросить", callback_data="reset_settings"),
            InlineKeyboardButton("✅ Готово", callback_data="close_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_param_keyboard(
    param_type: str, current_value: Union[float, int], default_value: Union[float, int]
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора значения параметра.

    Args:
        param_type: Тип параметра ("width", "height", "rows" или "columns")
        current_value: Текущее значение
        default_value: Значение по умолчанию

    Returns:
        InlineKeyboardMarkup: Клавиатура с вариантами значений
    """
    # Предустановленные значения
    if param_type == "width":
        values = [10, 20, 30, 40, 50, 60, 75, 80, 90, 100]
        label = "Ширина"
        unit = "мм"
    elif param_type == "height":
        values = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
        label = "Высота"
        unit = "мм"
    elif param_type == "rows":
        values = [5, 10, 15, 20]
        label = "Строк"
        unit = "шт"
    elif param_type == "columns":
        values = [1, 2, 3, 4, 5]
        label = "Колонок"
        unit = "шт"
    else:
        return InlineKeyboardMarkup([])

    buttons = []
    row = []
    for val in values:
        marker = "✓ " if val == current_value else ""
        callback_data = f"set_{param_type}_{val}"
        row.append(InlineKeyboardButton(f"{marker}{val}", callback_data=callback_data))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append(
        [
            InlineKeyboardButton(
                f"По умолчанию ({default_value})", callback_data=f"set_{param_type}_{default_value}"
            )
        ]
    )
    buttons.append([InlineKeyboardButton("◀️ Назад к настройкам", callback_data="back_to_settings")])

    return InlineKeyboardMarkup(buttons)
