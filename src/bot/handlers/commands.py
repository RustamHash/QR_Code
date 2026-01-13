"""
Обработчики команд бота.
"""
from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.repositories import (
    UserRepository, UserSettingsRepository, ProcessingHistoryRepository
)
from ...core.config import get_settings
from ...core.logging_config import get_logger
from ...core.exceptions import QRCodeBotException
from ..keyboards.settings import create_settings_keyboard
from .base import get_user_id, ensure_user_registered, get_user_settings_dict

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user_id = get_user_id(update)
    logger.info(f"Команда /start от пользователя {user_id}")
    
    try:
        db = next(get_db())
        try:
            # Регистрируем пользователя
            user = update.effective_user
            ensure_user_registered(update, db)
            
            # Получаем настройки
            settings = get_user_settings_dict(user_id, db)
            
            # Проверяем наличие телефона
            user_data = UserRepository.get_by_user_id(db, user_id)
            has_phone = user_data and user_data.phone_number
            
            # Формируем приветственное сообщение
            welcome_message = (
                "👋 Добро пожаловать в бот для генерации QR-кодов!\n\n"
                "📤 Отправьте Excel файл (.xlsx, .xls) или текстовое сообщение, "
                "и я создам PDF с QR-кодами.\n\n"
                "ℹ️ Для Excel: данные читаются из первой колонки.\n"
                "ℹ️ Для текста: одна строка = один QR-код, несколько строк = несколько QR-кодов.\n\n"
                f"⚙️ Ваши настройки PDF:\n"
                f"  • Ширина: {settings['width']} мм\n"
                f"  • Высота: {settings['height']} мм\n"
                f"  • Строк на странице: {settings['rows_per_page']}\n"
                f"  • Колонок на странице: {settings['columns_per_page']}\n\n"
                "💡 Используйте /settings для изменения настроек или /help для справки."
            )
            
            # Если нет телефона, предлагаем поделиться
            if not has_phone:
                keyboard = ReplyKeyboardMarkup(
                    [[KeyboardButton("📱 Поделиться контактом", request_contact=True)]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                welcome_message += "\n\n📱 Вы можете поделиться своим номером телефона:"
                await update.message.reply_text(welcome_message, reply_markup=keyboard)
            else:
                await update.message.reply_text(welcome_message, reply_markup=ReplyKeyboardRemove())
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=ReplyKeyboardRemove()
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    user_id = get_user_id(update)
    logger.info(f"Команда /help от пользователя {user_id}")
    
    try:
        help_text = (
            "📖 Справка по использованию бота:\n\n"
            "1️⃣ Отправьте Excel файл (.xlsx или .xls)\n"
            "   • Данные читаются из первой колонки\n"
            "   • Бот автоматически создаст PDF с QR-кодами\n\n"
            "2️⃣ Или отправьте текстовое сообщение\n"
            "   • Одна строка = один QR-код\n"
            "   • Несколько строк (через Enter) = несколько QR-кодов\n"
            "   • Используйте /text для явного указания режима\n\n"
            "⚙️ Настройки PDF:\n"
            "/settings - открыть меню настроек\n"
            "/width <значение> - ширина страницы в мм (по умолчанию: 75)\n"
            "/height <значение> - высота страницы в мм (по умолчанию: 120)\n"
            "/rows <значение> - количество строк на странице (по умолчанию: 5)\n"
            "/columns <значение> - количество колонок на странице (по умолчанию: 1)\n"
            "/reset - сбросить настройки к значениям по умолчанию\n\n"
            "📊 Дополнительно:\n"
            "/history - просмотреть историю обработки\n"
            "/stats - статистика (только для администратора)\n"
        )
        await update.message.reply_text(help_text)
    except Exception as e:
        logger.error(f"Ошибка в команде /help: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при отправке справки.")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /settings."""
    user_id = get_user_id(update)
    logger.info(f"Команда /settings от пользователя {user_id}")
    
    try:
        db = next(get_db())
        try:
            settings = get_user_settings_dict(user_id, db)
            
            settings_text = (
                f"⚙️ Настройки PDF:\n\n"
                f"📏 Ширина страницы: {settings['width']} мм\n"
                f"📐 Высота страницы: {settings['height']} мм\n"
                f"📊 Строк на странице: {settings['rows_per_page']}\n"
                f"📋 Колонок на странице: {settings['columns_per_page']}\n\n"
                f"Используйте кнопки ниже для изменения настроек:"
            )
            
            keyboard = create_settings_keyboard(settings)
            await update.message.reply_text(settings_text, reply_markup=keyboard)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка в команде /settings: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при отображении настроек.")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset."""
    user_id = get_user_id(update)
    logger.info(f"Команда /reset от пользователя {user_id}")
    
    try:
        db = next(get_db())
        try:
            config = get_settings()
            UserSettingsRepository.reset_to_default(db, user_id)
            
            await update.message.reply_text(
                f"✅ Настройки сброшены к значениям по умолчанию:\n"
                f"📏 Ширина: {config.default_width} мм\n"
                f"📐 Высота: {config.default_height} мм\n"
                f"📊 Строк на странице: {config.default_rows_per_page}\n"
                f"📋 Колонок на странице: {config.default_columns_per_page}"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка в команде /reset: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при сбросе настроек.")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /history."""
    user_id = get_user_id(update)
    logger.info(f"Команда /history от пользователя {user_id}")
    
    try:
        db = next(get_db())
        try:
            history_list = ProcessingHistoryRepository.get_by_user_id(db, user_id, limit=10)
            
            if not history_list:
                await update.message.reply_text("📋 История обработки пуста.")
                return
            
            history_text = "📋 История обработки (последние 10 записей):\n\n"
            
            for i, record in enumerate(history_list, 1):
                status_emoji = "✅" if record.status.value == "success" else "❌"
                type_emoji = "📄" if record.processing_type.value == "file" else "📝"
                
                history_text += (
                    f"{i}. {status_emoji} {type_emoji} {record.source_name}\n"
                    f"   QR-кодов: {record.qr_codes_count}\n"
                    f"   Дата: {record.processed_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
            
            await update.message.reply_text(history_text)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка в команде /history: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при получении истории.")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats (только для администратора)."""
    user_id = get_user_id(update)
    logger.info(f"Команда /stats от пользователя {user_id}")
    
    try:
        config = get_settings()
        
        # Проверяем, является ли пользователь администратором
        if not config.admin_id or user_id != config.admin_id:
            await update.message.reply_text("❌ Эта команда доступна только администратору.")
            return
        
        db = next(get_db())
        try:
            # Получаем статистику
            stats = ProcessingHistoryRepository.get_statistics(db)
            user_count = UserRepository.count(db)
            
            stats_text = (
                "📊 Статистика бота:\n\n"
                f"👥 Пользователей: {user_count}\n"
                f"📄 Всего обработок: {stats['total_processing']}\n"
                f"  ✅ Успешных: {stats['success_count']}\n"
                f"  ❌ Ошибок: {stats['error_count']}\n"
                f"📁 Обработок файлов: {stats['file_processing_count']}\n"
                f"📝 Обработок текста: {stats['text_processing_count']}\n"
                f"🔲 Всего QR-кодов создано: {stats['total_qr_codes']}"
            )
            
            await update.message.reply_text(stats_text)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Ошибка в команде /stats: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при получении статистики.")


async def set_width_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /width."""
    user_id = get_user_id(update)
    logger.info(f"Команда /width от пользователя {user_id}")
    
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите ширину в мм. Например: /width 75")
            return
        
        width = float(context.args[0])
        if width <= 0:
            raise ValueError("Ширина должна быть положительным числом")
        
        db = next(get_db())
        try:
            UserSettingsRepository.update(db, user_id, width=width)
            await update.message.reply_text(f"✅ Ширина страницы установлена: {width} мм")
        finally:
            db.close()
    except ValueError as e:
        await update.message.reply_text("❌ Неверное значение. Используйте положительное число.")
    except Exception as e:
        logger.error(f"Ошибка в команде /width: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при установке ширины.")


async def set_height_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /height."""
    user_id = get_user_id(update)
    logger.info(f"Команда /height от пользователя {user_id}")
    
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите высоту в мм. Например: /height 120")
            return
        
        height = float(context.args[0])
        if height <= 0:
            raise ValueError("Высота должна быть положительным числом")
        
        db = next(get_db())
        try:
            UserSettingsRepository.update(db, user_id, height=height)
            await update.message.reply_text(f"✅ Высота страницы установлена: {height} мм")
        finally:
            db.close()
    except ValueError as e:
        await update.message.reply_text("❌ Неверное значение. Используйте положительное число.")
    except Exception as e:
        logger.error(f"Ошибка в команде /height: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при установке высоты.")


async def set_rows_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /rows."""
    user_id = get_user_id(update)
    logger.info(f"Команда /rows от пользователя {user_id}")
    
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите количество строк на странице. Например: /rows 5")
            return
        
        rows = int(context.args[0])
        if rows <= 0:
            raise ValueError("Количество должно быть положительным числом")
        
        db = next(get_db())
        try:
            UserSettingsRepository.update(db, user_id, rows_per_page=rows)
            await update.message.reply_text(f"✅ Количество строк на странице установлено: {rows}")
        finally:
            db.close()
    except ValueError as e:
        await update.message.reply_text("❌ Неверное значение. Используйте целое положительное число.")
    except Exception as e:
        logger.error(f"Ошибка в команде /rows: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при установке количества строк.")


async def set_columns_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /columns."""
    user_id = get_user_id(update)
    logger.info(f"Команда /columns от пользователя {user_id}")
    
    try:
        if not context.args:
            await update.message.reply_text("❌ Укажите количество колонок на странице. Например: /columns 2")
            return
        
        columns = int(context.args[0])
        if columns <= 0:
            raise ValueError("Количество должно быть положительным числом")
        
        db = next(get_db())
        try:
            UserSettingsRepository.update(db, user_id, columns_per_page=columns)
            await update.message.reply_text(f"✅ Количество колонок на странице установлено: {columns}")
        finally:
            db.close()
    except ValueError as e:
        await update.message.reply_text("❌ Неверное значение. Используйте целое положительное число.")
    except Exception as e:
        logger.error(f"Ошибка в команде /columns: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при установке количества колонок.")


def setup_commands(application) -> None:
    """Настраивает команды бота."""
    async def post_init(app) -> None:
        await app.bot.set_my_commands([
            BotCommand("start", "Начать работу с ботом"),
            BotCommand("help", "Справка по использованию"),
            BotCommand("settings", "Настройки PDF"),
            BotCommand("history", "История обработки"),
        ])
        logger.info("Команды бота установлены")
    
    application.post_init = post_init

