"""
Обработчики callback-запросов от inline-кнопок.
"""

from telegram import Update
from telegram.ext import ContextTypes

from ...database.database import get_db
from ...database.repositories import UserSettingsRepository
from ...core.config import get_settings
from ...core.logging_config import get_logger
from ..keyboards.settings import create_settings_keyboard, create_param_keyboard
from .base import get_user_id, get_user_settings_dict

logger = get_logger(__name__)


async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback-запросов от кнопок настроек."""
    query = update.callback_query
    if not query:
        return

    user_id = get_user_id(update)
    await query.answer()

    logger.info(f"Callback от пользователя {user_id}: {query.data}")

    try:
        db = next(get_db())
        try:
            settings = get_user_settings_dict(user_id, db)
            config = get_settings()

            current_width = settings["width"]
            current_height = settings["height"]
            current_rows = settings["rows_per_page"]
            current_columns = settings["columns_per_page"]

            if query.data == "menu_width":
                text = f"📏 Выберите ширину страницы (текущее: {current_width} мм):"
                keyboard = create_param_keyboard("width", current_width, config.default_width)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "menu_height":
                text = f"📐 Выберите высоту страницы (текущее: {current_height} мм):"
                keyboard = create_param_keyboard("height", current_height, config.default_height)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "menu_rows":
                text = f"📊 Выберите количество строк на странице (текущее: {current_rows}):"
                keyboard = create_param_keyboard("rows", current_rows, config.default_rows_per_page)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "menu_columns":
                text = f"📋 Выберите количество колонок на странице (текущее: {current_columns}):"
                keyboard = create_param_keyboard(
                    "columns", current_columns, config.default_columns_per_page
                )
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data.startswith("set_width_"):
                value = float(query.data.split("_")[2])
                UserSettingsRepository.update(db, user_id, width=value)
                logger.info(f"Пользователь {user_id} установил ширину: {value} мм")
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {value} мм\n"
                    f"📐 Высота страницы: {current_height} мм\n"
                    f"📊 Строк на странице: {current_rows}\n"
                    f"📋 Колонок на странице: {current_columns}\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                settings["width"] = value
                keyboard = create_settings_keyboard(settings)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data.startswith("set_height_"):
                value = float(query.data.split("_")[2])
                UserSettingsRepository.update(db, user_id, height=value)
                logger.info(f"Пользователь {user_id} установил высоту: {value} мм")
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {current_width} мм\n"
                    f"📐 Высота страницы: {value} мм\n"
                    f"📊 Строк на странице: {current_rows}\n"
                    f"📋 Колонок на странице: {current_columns}\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                settings["height"] = value
                keyboard = create_settings_keyboard(settings)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data.startswith("set_rows_"):
                value = int(query.data.split("_")[2])
                UserSettingsRepository.update(db, user_id, rows_per_page=value)
                logger.info(f"Пользователь {user_id} установил количество строк: {value}")
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {current_width} мм\n"
                    f"📐 Высота страницы: {current_height} мм\n"
                    f"📊 Строк на странице: {value}\n"
                    f"📋 Колонок на странице: {current_columns}\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                settings["rows_per_page"] = value
                keyboard = create_settings_keyboard(settings)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data.startswith("set_columns_"):
                value = int(query.data.split("_")[2])
                UserSettingsRepository.update(db, user_id, columns_per_page=value)
                logger.info(f"Пользователь {user_id} установил количество колонок: {value}")
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {current_width} мм\n"
                    f"📐 Высота страницы: {current_height} мм\n"
                    f"📊 Строк на странице: {current_rows}\n"
                    f"📋 Колонок на странице: {value}\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                settings["columns_per_page"] = value
                keyboard = create_settings_keyboard(settings)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "reset_settings":
                UserSettingsRepository.reset_to_default(db, user_id)
                logger.info(f"Пользователь {user_id} сбросил настройки")
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {config.default_width} мм\n"
                    f"📐 Высота страницы: {config.default_height} мм\n"
                    f"📊 Строк на странице: {config.default_rows_per_page}\n"
                    f"📋 Колонок на странице: {config.default_columns_per_page}\n\n"
                    f"✅ Настройки сброшены к значениям по умолчанию!\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                keyboard = create_settings_keyboard(
                    {
                        "width": config.default_width,
                        "height": config.default_height,
                        "rows_per_page": config.default_rows_per_page,
                        "columns_per_page": config.default_columns_per_page,
                    }
                )
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "back_to_settings":
                settings = get_user_settings_dict(user_id, db)
                text = (
                    f"⚙️ Настройки PDF:\n\n"
                    f"📏 Ширина страницы: {settings['width']} мм\n"
                    f"📐 Высота страницы: {settings['height']} мм\n"
                    f"📊 Строк на странице: {settings['rows_per_page']}\n"
                    f"📋 Колонок на странице: {settings['columns_per_page']}\n\n"
                    f"Используйте кнопки ниже для изменения настроек:"
                )
                keyboard = create_settings_keyboard(settings)
                await query.edit_message_text(text, reply_markup=keyboard)

            elif query.data == "close_menu":
                await query.edit_message_text("✅ Настройки сохранены!")
                logger.info(f"Пользователь {user_id} закрыл меню настроек")
            else:
                logger.warning(f"Неизвестный callback: {query.data}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_settings_callback: {e}", exc_info=True)
        try:
            await query.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)
        except Exception:
            pass
