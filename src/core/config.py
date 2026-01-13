"""
Конфигурация приложения с использованием pydantic-settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Токен Telegram бота")
    admin_id: Optional[int] = Field(None, description="ID администратора")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///bot_database.db",
        description="URL базы данных"
    )
    
    # Application Settings
    max_file_size_mb: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Максимальный размер файла в MB"
    )
    max_text_length: int = Field(
        default=10000,
        ge=1,
        le=100000,
        description="Максимальная длина текста"
    )
    rate_limit_requests: int = Field(
        default=10,
        ge=1,
        description="Количество запросов для rate limiting"
    )
    rate_limit_period: int = Field(
        default=60,
        ge=1,
        description="Период rate limiting в секундах"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )
    log_file: str = Field(
        default="bot.log",
        description="Файл для логов"
    )
    
    # PDF Default Settings
    default_width: float = Field(
        default=75.0,
        ge=10.0,
        le=1000.0,
        description="Ширина страницы PDF по умолчанию (мм)"
    )
    default_height: float = Field(
        default=120.0,
        ge=10.0,
        le=1000.0,
        description="Высота страницы PDF по умолчанию (мм)"
    )
    default_rows_per_page: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Количество строк на странице по умолчанию"
    )
    default_columns_per_page: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Количество колонок на странице по умолчанию"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Валидация уровня логирования."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level должен быть одним из: {valid_levels}")
        return v.upper()
    
    @field_validator("telegram_bot_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Валидация токена бота."""
        if not v or len(v) < 10:
            raise ValueError("Токен бота не может быть пустым или слишком коротким")
        return v
    
    def get_max_file_size_bytes(self) -> int:
        """Возвращает максимальный размер файла в байтах."""
        return self.max_file_size_mb * 1024 * 1024


# Глобальный экземпляр настроек
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Получает экземпляр настроек (singleton).
    
    Returns:
        Settings: экземпляр настроек
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Перезагружает настройки из файла.
    
    Returns:
        Settings: новый экземпляр настроек
    """
    global _settings
    _settings = Settings()
    return _settings

