"""
Обработчики текстовых сообщений и файлов.
"""

import io
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from ...database.database import get_db
from ...database.repositories import UserRepository, UserFileRepository, ProcessingHistoryRepository
from ...database.models import ProcessingType, ProcessingStatus
from ...services.excel_service import read_data_from_excel
from ...services.text_service import process_text_message
from ...services.pdf_service import create_qr_pdf
from ...services.qr_decode_service import decode_qr_from_image
from ...services.file_service import validate_file, read_file_to_bytesio, get_safe_filename
from ...core.exceptions import (
    FileProcessingError,
    TextProcessingError,
    ValidationError,
    QRCodeBotException,
    RateLimitError,
    QRCodeDecodeError,
)
from ...core.logging_config import get_logger
from ...core.config import get_settings
from ..middleware.rate_limit import check_rate_limit
from .base import get_user_id, ensure_user_registered, get_user_settings_dict

logger = get_logger(__name__)


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик получения контакта от пользователя."""
    user_id = get_user_id(update)
    contact = update.message.contact

    try:
        if contact and contact.user_id == user_id:
            phone_number = contact.phone_number
            db = next(get_db())
            try:
                UserRepository.update_phone(db, user_id, phone_number)
                logger.info(f"Номер телефона пользователя {user_id} сохранен")
                await update.message.reply_text(
                    "✅ Спасибо! Ваш номер телефона сохранен.", reply_markup=ReplyKeyboardRemove()
                )
            finally:
                db.close()
        else:
            await update.message.reply_text(
                "❌ Пожалуйста, поделитесь своим контактом.", reply_markup=ReplyKeyboardRemove()
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке контакта: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при сохранении контакта.", reply_markup=ReplyKeyboardRemove()
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик загрузки документов (Excel файлов)."""
    user_id = get_user_id(update)
    document = update.message.document
    processing_msg = None

    try:
        # Проверка rate limit
        check_rate_limit(user_id)

        if not document:
            await update.message.reply_text("❌ Файл не найден.")
            return

        file_name = document.file_name or "unknown"
        logger.info(f"Получен файл от пользователя {user_id}: {file_name}")

        # Валидация расширения
        if not file_name.lower().endswith((".xlsx", ".xls")):
            await update.message.reply_text("❌ Поддерживаются только Excel файлы (.xlsx, .xls)")
            return

        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text("⏳ Обработка файла...")

        # Получаем файл
        file = await context.bot.get_file(document.file_id)
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_data = file_bytes.getvalue()

        # Валидация файла
        validate_file(file_name, file_data)

        # Регистрируем пользователя
        db = next(get_db())
        try:
            ensure_user_registered(update, db)

            # Сохраняем файл в БД
            safe_filename = get_safe_filename(file_name)
            UserFileRepository.create(db, user_id, safe_filename, file_data)

            # Читаем данные из Excel
            await processing_msg.edit_text("📖 Чтение данных из Excel...")
            file_bytes.seek(0)
            data = read_data_from_excel(file_bytes)

            if not data:
                await processing_msg.edit_text("❌ Не найдено данных в первой колонке!")
                ProcessingHistoryRepository.create(
                    db,
                    user_id,
                    ProcessingType.FILE,
                    safe_filename,
                    0,
                    ProcessingStatus.ERROR,
                    "Не найдено данных",
                )
                return

            logger.info(f"Прочитано {len(data)} записей из файла пользователя {user_id}")

            # Получаем настройки пользователя
            settings = get_user_settings_dict(user_id, db)

            # Создаем PDF
            await processing_msg.edit_text(f"🔲 Генерация QR-кодов для {len(data)} записей...")
            pdf_buffer = create_qr_pdf(
                data,
                width=settings["width"],
                height=settings["height"],
                rows_per_page=settings["rows_per_page"],
                columns_per_page=settings["columns_per_page"],
            )

            # Сохраняем в историю
            ProcessingHistoryRepository.create(
                db, user_id, ProcessingType.FILE, safe_filename, len(data), ProcessingStatus.SUCCESS
            )

            # Отправляем PDF
            await processing_msg.edit_text("📤 Отправка файла...")
            await update.message.reply_document(
                document=pdf_buffer,
                filename="qr_codes.pdf",
                caption=f"✅ Создано {len(data)} QR-кодов",
            )

            await processing_msg.delete()
            logger.info(f"PDF файл успешно отправлен пользователю {user_id}")

        finally:
            db.close()

    except RateLimitError as e:
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")
    except ValidationError as e:
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")
    except FileProcessingError as e:
        logger.error(f"Ошибка обработки файла: {e}", exc_info=True)
        if processing_msg:
            await processing_msg.edit_text(f"❌ Ошибка обработки файла: {str(e)}")
        else:
            await update.message.reply_text(f"❌ Ошибка обработки файла: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке файла: {e}", exc_info=True)
        error_msg = f"❌ Ошибка при обработке файла: {str(e)}"
        try:
            if processing_msg:
                await processing_msg.edit_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
        except Exception:
            pass


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    user_id = get_user_id(update)
    text = update.message.text

    # Игнорируем команды
    if text and text.startswith("/"):
        return

    processing_msg = None

    try:
        # Проверка rate limit
        check_rate_limit(user_id)

        if not text or not text.strip():
            await update.message.reply_text("❌ Сообщение пусто.")
            return

        logger.info(f"Получено текстовое сообщение от пользователя {user_id}")

        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text("⏳ Обработка текста...")

        # Обрабатываем текст
        data, is_single_line = process_text_message(text)

        # Регистрируем пользователя
        db = next(get_db())
        try:
            ensure_user_registered(update, db)

            # Получаем настройки пользователя
            settings = get_user_settings_dict(user_id, db)

            # Создаем PDF
            await processing_msg.edit_text(
                f"🔲 Генерация QR-кодов для {len(data)} {'строки' if len(data) == 1 else 'строк'}..."
            )
            pdf_buffer = create_qr_pdf(
                data,
                width=settings["width"],
                height=settings["height"],
                rows_per_page=settings["rows_per_page"],
                columns_per_page=settings["columns_per_page"],
            )

            # Сохраняем в историю
            source_name = "text (одна строка)" if is_single_line else f"text ({len(data)} строк)"
            ProcessingHistoryRepository.create(
                db, user_id, ProcessingType.TEXT, source_name, len(data), ProcessingStatus.SUCCESS
            )

            # Отправляем PDF
            await processing_msg.edit_text("📤 Отправка файла...")
            await update.message.reply_document(
                document=pdf_buffer,
                filename="qr_codes.pdf",
                caption=f"✅ Создано {len(data)} QR-код{'ов' if len(data) > 1 else ''}",
            )

            await processing_msg.delete()
            logger.info(f"PDF файл успешно отправлен пользователю {user_id}")

        finally:
            db.close()

    except RateLimitError as e:
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")
    except ValidationError as e:
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")
    except TextProcessingError as e:
        logger.error(f"Ошибка обработки текста: {e}", exc_info=True)
        if processing_msg:
            await processing_msg.edit_text(f"❌ Ошибка обработки текста: {str(e)}")
        else:
            await update.message.reply_text(f"❌ Ошибка обработки текста: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке текста: {e}", exc_info=True)
        error_msg = f"❌ Ошибка при обработке текста: {str(e)}"
        try:
            if processing_msg:
                await processing_msg.edit_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
        except Exception:
            pass


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик получения фото с QR-кодами."""
    user_id = get_user_id(update)
    photos = update.message.photo
    processing_msg = None

    try:
        # Проверка rate limit
        check_rate_limit(user_id)

        if not photos:
            await update.message.reply_text("❌ Фото не найдено.")
            return

        logger.info(f"Получено фото от пользователя {user_id}")

        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text("⏳ Обработка изображения...")

        # Получаем самое большое фото (обычно последнее в списке)
        photo = photos[-1]

        # Получаем файл фото
        file = await context.bot.get_file(photo.file_id)
        image_bytes = io.BytesIO()
        await file.download_to_memory(image_bytes)
        image_data = image_bytes.getvalue()

        # Декодируем QR-код
        await processing_msg.edit_text("🔍 Декодирование QR-кода...")
        decoded_data_list = decode_qr_from_image(image_data)

        if not decoded_data_list:
            await processing_msg.edit_text("❌ QR-код не найден на изображении.")
            return

        # Регистрируем пользователя
        db = next(get_db())
        try:
            ensure_user_registered(update, db)

            # Сохраняем в историю
            for i, decoded_data in enumerate(decoded_data_list, 1):
                source_name = f"QR decode ({i}/{len(decoded_data_list)})"
                ProcessingHistoryRepository.create(
                    db, user_id, ProcessingType.QR_DECODE, source_name, 1, ProcessingStatus.SUCCESS
                )

            # Отправляем результаты
            await processing_msg.edit_text("✅ QR-код успешно декодирован!")

            if len(decoded_data_list) == 1:
                # Один QR-код - отправляем данные
                decoded_data = decoded_data_list[0]
                # Ограничиваем длину сообщения
                if len(decoded_data) > 4000:
                    await update.message.reply_text(
                        f"📄 Данные из QR-кода (первые 4000 символов):\n\n{decoded_data[:4000]}...\n\n"
                        f"Полная длина: {len(decoded_data)} символов"
                    )
                else:
                    await update.message.reply_text(
                        f"📄 Данные из QR-кода:\n\n`{decoded_data}`", parse_mode="Markdown"
                    )
            else:
                # Несколько QR-кодов
                result_text = f"📄 Найдено {len(decoded_data_list)} QR-код(ов):\n\n"
                for i, decoded_data in enumerate(decoded_data_list, 1):
                    preview = (
                        decoded_data[:100] + "..." if len(decoded_data) > 100 else decoded_data
                    )
                    result_text += f"{i}. `{preview}`\n\n"

                if len(result_text) > 4000:
                    result_text = result_text[:4000] + "..."

                await update.message.reply_text(result_text, parse_mode="Markdown")

            await processing_msg.delete()
            logger.info(
                f"QR-код успешно декодирован для пользователя {user_id}: {len(decoded_data_list)} код(ов)"
            )

        finally:
            db.close()

    except QRCodeDecodeError as e:
        logger.error(f"Ошибка декодирования QR-кода: {e}", exc_info=True)
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")

        # Сохраняем ошибку в историю
        db = next(get_db())
        try:
            ensure_user_registered(update, db)
            ProcessingHistoryRepository.create(
                db, user_id, ProcessingType.QR_DECODE, "photo", 0, ProcessingStatus.ERROR, str(e)
            )
        finally:
            db.close()

    except RateLimitError as e:
        if processing_msg:
            await processing_msg.edit_text(f"❌ {str(e)}")
        else:
            await update.message.reply_text(f"❌ {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке фото: {e}", exc_info=True)
        error_msg = f"❌ Ошибка при обработке фото: {str(e)}"
        try:
            if processing_msg:
                await processing_msg.edit_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
        except Exception:
            pass
