"""
Репозитории для работы с данными.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..core.logging_config import get_logger
from .models import (
    User,
    UserSettings,
    UserFile,
    ProcessingHistory,
    ProcessingType,
    ProcessingStatus,
)

logger = get_logger(__name__)


class UserRepository:
    """Репозиторий для работы с пользователями."""

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[User]:
        """Получает пользователя по Telegram user_id."""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        """Создает нового пользователя."""
        user = User(user_id=user_id, first_name=first_name, last_name=last_name, username=username)
        db.add(user)

        # Создаем настройки по умолчанию
        settings = UserSettings(user_id=user_id)
        db.add(settings)

        db.commit()
        db.refresh(user)
        logger.info(f"Создан новый пользователь: {user_id}")
        return user

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Optional[User]:
        """Обновляет данные пользователя."""
        user = UserRepository.get_by_user_id(db, user_id)
        if user:
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if username is not None:
                user.username = username
            db.commit()
            db.refresh(user)
            logger.info(f"Обновлен пользователь: {user_id}")
        return user

    @staticmethod
    def update_phone(db: Session, user_id: int, phone_number: str) -> bool:
        """Обновляет номер телефона пользователя."""
        user = UserRepository.get_by_user_id(db, user_id)
        if user:
            user.phone_number = phone_number
            db.commit()
            logger.info(f"Обновлен номер телефона пользователя: {user_id}")
            return True
        return False

    @staticmethod
    def get_or_create(
        db: Session,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Tuple[User, bool]:
        """Получает или создает пользователя."""
        user = UserRepository.get_by_user_id(db, user_id)
        if user:
            # Обновляем данные, если они изменились
            updated = False
            if first_name is not None and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name is not None and user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if username is not None and user.username != username:
                user.username = username
                updated = True
            if updated:
                db.commit()
                db.refresh(user)
            return user, False
        else:
            user = UserRepository.create(db, user_id, first_name, last_name, username)
            return user, True

    @staticmethod
    def count(db: Session) -> int:
        """Возвращает количество пользователей."""
        return db.query(User).count()


class UserSettingsRepository:
    """Репозиторий для работы с настройками пользователей."""

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[UserSettings]:
        """Получает настройки пользователя."""
        return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    @staticmethod
    def get_or_create_default(db: Session, user_id: int) -> UserSettings:
        """Получает или создает настройки по умолчанию."""
        settings = UserSettingsRepository.get_by_user_id(db, user_id)
        if not settings:
            from ..core.config import get_settings

            config = get_settings()
            settings = UserSettings(
                user_id=user_id,
                width=config.default_width,
                height=config.default_height,
                rows_per_page=config.default_rows_per_page,
                columns_per_page=config.default_columns_per_page,
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings

    @staticmethod
    def update(
        db: Session,
        user_id: int,
        width: Optional[float] = None,
        height: Optional[float] = None,
        rows_per_page: Optional[int] = None,
        columns_per_page: Optional[int] = None,
    ) -> Optional[UserSettings]:
        """Обновляет настройки пользователя."""
        settings = UserSettingsRepository.get_or_create_default(db, user_id)

        if width is not None:
            settings.width = width
        if height is not None:
            settings.height = height
        if rows_per_page is not None:
            settings.rows_per_page = rows_per_page
        if columns_per_page is not None:
            settings.columns_per_page = columns_per_page

        db.commit()
        db.refresh(settings)
        logger.info(f"Обновлены настройки пользователя: {user_id}")
        return settings

    @staticmethod
    def reset_to_default(db: Session, user_id: int) -> UserSettings:
        """Сбрасывает настройки к значениям по умолчанию."""
        from ..core.config import get_settings

        config = get_settings()
        return UserSettingsRepository.update(
            db,
            user_id,
            width=config.default_width,
            height=config.default_height,
            rows_per_page=config.default_rows_per_page,
            columns_per_page=config.default_columns_per_page,
        )

    @staticmethod
    def get_dict(db: Session, user_id: int) -> Dict[str, Any]:
        """Возвращает настройки в виде словаря."""
        settings = UserSettingsRepository.get_or_create_default(db, user_id)
        return {
            "width": settings.width,
            "height": settings.height,
            "rows_per_page": settings.rows_per_page,
            "columns_per_page": settings.columns_per_page,
        }


class UserFileRepository:
    """Репозиторий для работы с файлами пользователей."""

    @staticmethod
    def create(db: Session, user_id: int, file_name: str, file_data: bytes) -> UserFile:
        """Создает запись о файле."""
        file_size = len(file_data)
        user_file = UserFile(
            user_id=user_id, file_name=file_name, file_data=file_data, file_size=file_size
        )
        db.add(user_file)
        db.commit()
        db.refresh(user_file)
        logger.info(f"Сохранен файл {file_name} для пользователя {user_id}")
        return user_file

    @staticmethod
    def get_by_id(db: Session, file_id: int) -> Optional[UserFile]:
        """Получает файл по ID."""
        return db.query(UserFile).filter(UserFile.id == file_id).first()

    @staticmethod
    def count_by_user_id(db: Session, user_id: int) -> int:
        """Возвращает количество файлов пользователя."""
        return db.query(UserFile).filter(UserFile.user_id == user_id).count()

    @staticmethod
    def get_total_size_by_user_id(db: Session, user_id: int) -> int:
        """Возвращает общий размер файлов пользователя в байтах."""
        result = db.query(func.sum(UserFile.file_size)).filter(UserFile.user_id == user_id).scalar()
        return result or 0


class ProcessingHistoryRepository:
    """Репозиторий для работы с историей обработки."""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        processing_type: ProcessingType,
        source_name: str,
        qr_codes_count: int,
        status: ProcessingStatus = ProcessingStatus.SUCCESS,
        error_message: Optional[str] = None,
    ) -> ProcessingHistory:
        """Создает запись в истории обработки."""
        history = ProcessingHistory(
            user_id=user_id,
            processing_type=processing_type,
            source_name=source_name,
            qr_codes_count=qr_codes_count,
            status=status,
            error_message=error_message,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        logger.info(
            f"Создана запись истории: user_id={user_id}, "
            f"type={processing_type}, count={qr_codes_count}"
        )
        return history

    @staticmethod
    def get_by_user_id(
        db: Session, user_id: int, limit: int = 50, offset: int = 0
    ) -> List[ProcessingHistory]:
        """Получает историю обработки пользователя."""
        return (
            db.query(ProcessingHistory)
            .filter(ProcessingHistory.user_id == user_id)
            .order_by(desc(ProcessingHistory.processed_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_by_user_id(db: Session, user_id: int) -> int:
        """Возвращает количество записей истории пользователя."""
        return db.query(ProcessingHistory).filter(ProcessingHistory.user_id == user_id).count()

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """Возвращает общую статистику обработки."""
        total_count = db.query(ProcessingHistory).count()
        success_count = (
            db.query(ProcessingHistory)
            .filter(ProcessingHistory.status == ProcessingStatus.SUCCESS)
            .count()
        )
        error_count = (
            db.query(ProcessingHistory)
            .filter(ProcessingHistory.status == ProcessingStatus.ERROR)
            .count()
        )

        total_qr_codes = db.query(func.sum(ProcessingHistory.qr_codes_count)).scalar() or 0

        file_count = (
            db.query(ProcessingHistory)
            .filter(ProcessingHistory.processing_type == ProcessingType.FILE)
            .count()
        )

        text_count = (
            db.query(ProcessingHistory)
            .filter(ProcessingHistory.processing_type == ProcessingType.TEXT)
            .count()
        )

        return {
            "total_processing": total_count,
            "success_count": success_count,
            "error_count": error_count,
            "total_qr_codes": total_qr_codes,
            "file_processing_count": file_count,
            "text_processing_count": text_count,
        }
