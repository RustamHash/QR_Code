# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Устанавливаем системные зависимости (включая libzbar0 для pyzbar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Создаем рабочую директорию
WORKDIR /app

# Копируем установленные пакеты из builder (system-wide)
COPY --from=builder /usr/local /usr/local

# Копируем код приложения
COPY . .

# Создаем пользователя для запуска приложения
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Переключаемся на пользователя
USER botuser

# Команда запуска
CMD ["python", "main.py"]

