# Multi-stage build для оптимизации размера образа
FROM python:3.11-slim as builder

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные пакеты из builder
COPY --from=builder /root/.local /root/.local

# Устанавливаем переменные окружения
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Создаем рабочую директорию
WORKDIR /app

# Копируем код приложения
COPY . .

# Создаем пользователя для запуска приложения
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Переключаемся на пользователя
USER botuser

# Команда запуска
CMD ["python", "main.py"]

