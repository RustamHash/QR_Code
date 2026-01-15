"""
Модели базы данных SQLAlchemy.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, LargeBinary, DateTime,
    ForeignKey, Index, Text, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ProcessingType(str, enum.Enum):
    """Тип обработки данных."""
    FILE = "file"
    TEXT = "text"
    QR_DECODE = "qr_decode"


class ProcessingStatus(str, enum.Enum):
    """Статус обработки."""
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"


class User(Base):
    """Модель пользователя Telegram."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    phone_number = Column(String(50))
    registered_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    settings = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    files = relationship(
        "UserFile",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    processing_history = relationship(
        "ProcessingHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserSettings(Base):
    """Модель настроек пользователя."""
    __tablename__ = 'user_settings'
    
    user_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )
    width = Column(Float, default=75.0, nullable=False)
    height = Column(Float, default=120.0, nullable=False)
    rows_per_page = Column(Integer, default=5, nullable=False)
    columns_per_page = Column(Integer, default=1, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    user = relationship("User", back_populates="settings")


class UserFile(Base):
    """Модель файла пользователя."""
    __tablename__ = 'user_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    file_name = Column(String(500), nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Связи
    user = relationship("User", back_populates="files")


class ProcessingHistory(Base):
    """Модель истории обработки."""
    __tablename__ = 'processing_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    processing_type = Column(
        SQLEnum(ProcessingType),
        nullable=False,
        index=True
    )
    source_name = Column(String(500))  # Имя файла или "text"
    qr_codes_count = Column(Integer, nullable=False, default=0)
    status = Column(
        SQLEnum(ProcessingStatus),
        nullable=False,
        default=ProcessingStatus.SUCCESS,
        index=True
    )
    error_message = Column(Text)
    processed_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Связи
    user = relationship("User", back_populates="processing_history")


# Создаем индексы для оптимизации
Index('idx_processing_history_user_type', ProcessingHistory.user_id, ProcessingHistory.processing_type)
Index('idx_processing_history_processed_at', ProcessingHistory.processed_at)

