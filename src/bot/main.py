"""
Главный модуль Telegram бота.
"""
import os
import sys
from pathlib import Path

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from ..core.config import get_settings, ConfigurationError
from ..core.logging_config import setup_logging, get_logger
from ..database.database import init_database
from .handlers import (
    commands, callbacks, messages
)

logger = get_logger(__name__)


def create_application() -> Application:
    """
    Создает и настраивает приложение Telegram бота.
    
    Returns:
        Application: Настроенное приложение
    
    Raises:
        ConfigurationError: если конфигурация невалидна
    """
    try:
        settings = get_settings()
        token = settings.telegram_bot_token
        
        if not token:
            raise ConfigurationError("Токен бота не указан в конфигурации")
        
        # Создаем приложение
        application = Application.builder().token(token).build()
        
        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", commands.start_command))
        application.add_handler(CommandHandler("help", commands.help_command))
        application.add_handler(CommandHandler("settings", commands.settings_command))
        application.add_handler(CommandHandler("reset", commands.reset_command))
        application.add_handler(CommandHandler("history", commands.history_command))
        application.add_handler(CommandHandler("stats", commands.stats_command))
        application.add_handler(CommandHandler("width", commands.set_width_command))
        application.add_handler(CommandHandler("height", commands.set_height_command))
        application.add_handler(CommandHandler("rows", commands.set_rows_command))
        application.add_handler(CommandHandler("columns", commands.set_columns_command))
        
        # Регистрируем обработчики callback
        application.add_handler(CallbackQueryHandler(callbacks.handle_settings_callback))
        
        # Регистрируем обработчики сообщений
        application.add_handler(MessageHandler(filters.CONTACT, messages.handle_contact))
        application.add_handler(MessageHandler(filters.Document.ALL, messages.handle_document))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_text_message))
        
        # Настраиваем команды бота
        commands.setup_commands(application)
        
        logger.info("Приложение бота создано и настроено")
        return application
        
    except ConfigurationError:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании приложения: {e}", exc_info=True)
        raise ConfigurationError(f"Не удалось создать приложение: {e}") from e


async def post_init(application: Application) -> None:
    """
    Функция инициализации после запуска бота.
    
    Args:
        application: Приложение бота
    """
    settings = get_settings()
    
    # Отправляем уведомление администратору
    if settings.admin_id:
        try:
            await application.bot.send_message(
                chat_id=settings.admin_id,
                text="✅ Бот запущен и готов к работе!"
            )
            logger.info(f"Уведомление отправлено администратору {settings.admin_id}")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление администратору: {e}")
    
    logger.info("Бот запущен и готов к работе")


async def post_shutdown(application: Application) -> None:
    """
    Функция завершения работы бота.
    
    Args:
        application: Приложение бота
    """
    settings = get_settings()
    
    # Отправляем уведомление администратору
    if settings.admin_id:
        try:
            await application.bot.send_message(
                chat_id=settings.admin_id,
                text="❌ Бот остановлен."
            )
            logger.info(f"Уведомление об остановке отправлено администратору {settings.admin_id}")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление администратору: {e}")
    
    logger.info("Бот остановлен")


def main() -> None:
    """Главная функция запуска бота."""
    try:
        # Настраиваем логирование
        setup_logging()
        logger.info("=" * 50)
        logger.info("Запуск QR Code Generator Bot")
        logger.info("=" * 50)
        
        # Инициализируем базу данных
        init_database()
        
        # Создаем приложение
        application = create_application()
        
        # Устанавливаем обработчики событий
        application.post_init = post_init
        application.post_shutdown = post_shutdown
        
        # Запускаем бота
        logger.info("Бот запускается...")
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (KeyboardInterrupt)")
    except ConfigurationError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        print(f"\n❌ Ошибка конфигурации: {e}")
        print("Проверьте файл .env или переменные окружения.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}", exc_info=True)
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

