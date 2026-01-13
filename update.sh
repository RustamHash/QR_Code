#!/bin/bash
# Скрипт обновления QR Code Bot

set -e

PROJECT_DIR="/opt/qr_code_bot"
SERVICE_NAME="qr-code-bot"

echo "🔄 Обновление QR Code Bot..."

cd "$PROJECT_DIR"

# Обновление кода
echo "📥 Получение обновлений из репозитория..."
git pull origin main

# Обновление зависимостей
echo "📦 Обновление зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Применение миграций
echo "🗄️  Применение миграций базы данных..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
fi

# Перезапуск службы
echo "🔄 Перезапуск службы..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ Обновление завершено!"
echo "📊 Статус:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l

