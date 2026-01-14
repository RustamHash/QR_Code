"""
Инициализация и настройка базы данных.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from ..core.config import get_settings
from ..core.logging_config import get_logger
from .models import Base

logger = get_logger(__name__)

_settings = get_settings()
_engine = None
_SessionLocal = None


def get_engine():
    """
    Получает или создает движок SQLAlchemy.
    
    Returns:
        Engine: движок SQLAlchemy
    """
    global _engine
    if _engine is None:
        database_url = _settings.database_url
        
        # Для SQLite используем StaticPool для лучшей работы с потоками
        if database_url.startswith("sqlite"):
            # Обрабатываем относительные пути для SQLite
            if database_url.startswith("sqlite:///"):
                db_path = database_url.replace("sqlite:///", "")
                # Преобразуем в абсолютный путь
                if not os.path.isabs(db_path):
                    db_path = os.path.abspath(db_path)
                
                # Проверяем, не является ли путь директорией (ошибка конфигурации)
                if os.path.exists(db_path) and os.path.isdir(db_path):
                    logger.error(f"Путь к базе данных является директорией: {db_path}")
                    raise ValueError(f"Путь к базе данных является директорией: {db_path}. Удалите директорию и попробуйте снова.")
                
                # Создаем директорию для БД, если нужно
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                    except Exception as e:
                        logger.warning(f"Не удалось создать директорию для БД: {e}")
                
                # Используем абсолютный путь
                database_url = f"sqlite:///{db_path}"
            
            _engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False
            )
        else:
            _engine = create_engine(
                database_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=False
            )
        
        logger.info(f"Движок базы данных создан: {database_url}")
    
    return _engine


def get_session_local():
    """
    Получает или создает фабрику сессий.
    
    Returns:
        sessionmaker: фабрика сессий
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        logger.info("Фабрика сессий создана")
    
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Генератор для получения сессии базы данных (dependency injection).
    
    Yields:
        Session: сессия базы данных
    """
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Инициализирует базу данных, создает все таблицы.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}", exc_info=True)
        raise


def close_database():
    """
    Закрывает соединения с базой данных.
    """
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None
        logger.info("Соединения с базой данных закрыты")

