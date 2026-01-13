#!/bin/bash
# Финальный скрипт развертывания с автоматической настройкой
set -e

echo "🚀 Развертывание QR Code Bot на Beget Cloud..."

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка пакетов
echo "📦 Установка пакетов..."
apt install -y python3 python3-pip python3-venv git

# Создание директории
echo "📁 Создание директории проекта..."
mkdir -p /opt/qr_code_bot
cd /opt/qr_code_bot

# Клонирование репозитория
if [ -d .git ]; then
    echo "🔄 Обновление кода..."
    git pull origin main
else
    echo "📥 Клонирование репозитория..."
    git clone https://github.com/RustamHash/QR_Code.git .
fi

# Виртуальное окружение
if [ ! -d venv ]; then
    echo "🐍 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Установка зависимостей
echo "📦 Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла
echo "⚙️ Настройка .env файла..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Будет настроен вручную или через переменные окружения
fi

# Применение миграций
echo "🗄️ Применение миграций..."
alembic upgrade head

# Установка systemd service
echo "🔧 Установка systemd service..."
cp qr-code-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qr-code-bot

echo "✅ Развертывание завершено!"
echo ""
echo "⚠️ ВАЖНО: Отредактируйте .env файл перед запуском:"
echo "   nano /opt/qr_code_bot/.env"
echo ""
echo "Затем запустите:"
echo "   systemctl start qr-code-bot"
echo "   systemctl status qr-code-bot"

