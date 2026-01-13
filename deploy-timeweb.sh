#!/bin/bash
# Скрипт развертывания QR Code Bot на Timeweb Cloud
set -e

echo "🚀 Развертывание QR Code Bot на Timeweb Cloud..."

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка пакетов
echo "📦 Установка пакетов..."
apt install -y python3 python3-pip python3-venv git curl wget unzip

# Создание директории
echo "📁 Создание директории проекта..."
mkdir -p /opt/qr_code_bot
cd /opt/qr_code_bot

# Скачивание проекта через зеркало
echo "📥 Скачивание проекта..."
if command -v curl &> /dev/null; then
    curl -L https://ghproxy.com/https://github.com/RustamHash/QR_Code/archive/refs/heads/main.zip -o qr_code.zip
elif command -v wget &> /dev/null; then
    wget https://ghproxy.com/https://github.com/RustamHash/QR_Code/archive/refs/heads/main.zip -O qr_code.zip
else
    echo "❌ Не найдено curl или wget"
    exit 1
fi

# Распаковка
echo "📦 Распаковка проекта..."
unzip -q qr_code.zip
mv QR_Code-main/* .
mv QR_Code-main/.* . 2>/dev/null || true
rmdir QR_Code-main
rm qr_code.zip

# Виртуальное окружение
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла
echo "⚙️ Настройка .env файла..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  ВНИМАНИЕ: Отредактируйте файл .env и укажите TELEGRAM_BOT_TOKEN!"
    echo "   nano /opt/qr_code_bot/.env"
fi

# Применение миграций
echo "🗄️ Применение миграций..."
alembic upgrade head

# Установка systemd service
echo "🔧 Установка systemd service..."
cp qr-code-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qr-code-bot.service

echo "✅ Развертывание завершено!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env: nano /opt/qr_code_bot/.env"
echo "2. Запустите бота: systemctl start qr-code-bot"
echo "3. Проверьте статус: systemctl status qr-code-bot"

