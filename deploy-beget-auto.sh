#!/bin/bash
# Автоматическое развертывание QR Code Bot на Beget Cloud
# Использование: ./deploy-beget-auto.sh

set -e

echo "🚀 Начало автоматического развертывания QR Code Bot на Beget..."

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Директория проекта
PROJECT_DIR="/opt/qr_code_bot"

# 1. Обновление системы
echo -e "${YELLOW}📦 Обновление системы...${NC}"
apt update
apt upgrade -y

# 2. Установка необходимых пакетов
echo -e "${YELLOW}📦 Установка пакетов...${NC}"
apt install -y python3 python3-pip python3-venv git

# Проверка версии Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python версия: $PYTHON_VERSION${NC}"

# 3. Создание директории проекта
echo -e "${YELLOW}📁 Создание директории проекта...${NC}"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 4. Клонирование репозитория
if [ -d ".git" ]; then
    echo -e "${YELLOW}🔄 Обновление кода из репозитория...${NC}"
    git pull origin main
else
    echo -e "${YELLOW}📥 Клонирование репозитория...${NC}"
    git clone https://github.com/RustamHash/QR_Code.git .
fi

# 5. Создание виртуального окружения
echo -e "${YELLOW}🐍 Создание виртуального окружения...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 6. Активация и установка зависимостей
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Создание .env файла (если не существует)
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️ Создание .env файла...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  ВНИМАНИЕ: Отредактируйте файл .env и укажите TELEGRAM_BOT_TOKEN!${NC}"
    echo -e "${YELLOW}   nano $PROJECT_DIR/.env${NC}"
    echo ""
    echo "Нажмите Enter после редактирования .env файла..."
    read
fi

# 8. Применение миграций
echo -e "${YELLOW}🗄️  Применение миграций базы данных...${NC}"
alembic upgrade head

# 9. Установка systemd service
echo -e "${YELLOW}🔧 Установка systemd service...${NC}"
cp qr-code-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qr-code-bot.service

# 10. Запуск бота
echo -e "${YELLOW}🚀 Запуск бота...${NC}"
systemctl start qr-code-bot.service

# 11. Проверка статуса
echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo -e "${YELLOW}Статус службы:${NC}"
systemctl status qr-code-bot.service --no-pager -l

echo ""
echo -e "${YELLOW}Полезные команды:${NC}"
echo "  Просмотр логов: journalctl -u qr-code-bot -f"
echo "  Перезапуск: systemctl restart qr-code-bot"
echo "  Остановка: systemctl stop qr-code-bot"
echo "  Статус: systemctl status qr-code-bot"

