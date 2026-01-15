"""
Базовые функции для обработчиков.
"""

from typing import Optional
from telegram import Update
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.repositories import UserRepository, UserSettingsRepository
from ...core.logging_config import get_logger

logger = get_logger(__name__)


def get_user_id(update: Update) -> int:
    """
    Получает ID пользователя из update.

    Args:
        update: Объект Update от Telegram

    Returns:
        int: ID пользователя
    """
    if update.effective_user:
        return update.effective_user.id
    return 0


def ensure_user_registered(update: Update, db: Session) -> None:
    """
    Убеждается, что пользователь зарегистрирован в базе данных.

    Args:
        update: Объект Update от Telegram
        db: Сессия базы данных
    """
    user = update.effective_user
    if not user:
        return

    UserRepository.get_or_create(
        db, user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    )


def get_user_settings_dict(user_id: int, db: Session) -> dict:
    """
    Получает настройки пользователя в виде словаря.

    Args:
        user_id: ID пользователя
        db: Сессия базы данных

    Returns:
        dict: Словарь с настройками
    """
    return UserSettingsRepository.get_dict(db, user_id)
