#!/bin/bash
# Скрипт развертывания QR Code Bot на VPS

set -e

echo "🚀 Начало развертывания QR Code Bot..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не установлен. Установите Python 3.10 или выше.${NC}"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Требуется Python 3.10 или выше. Текущая версия: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python найден: $(python3 --version)${NC}"

# Создание директории для проекта (если не существует)
PROJECT_DIR="/opt/qr_code_bot"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📁 Создание директории проекта: $PROJECT_DIR${NC}"
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

# Клонирование или обновление репозитория
if [ -d "$PROJECT_DIR/.git" ]; then
    echo -e "${YELLOW}🔄 Обновление кода из репозитория...${NC}"
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo -e "${YELLOW}📥 Клонирование репозитория...${NC}"
    git clone https://github.com/RustamHash/QR_Code.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Создание виртуального окружения
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${YELLOW}🐍 Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# Активация виртуального окружения и установка зависимостей
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env файла (если не существует)
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚙️ Создание файла .env из примера...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  ВНИМАНИЕ: Отредактируйте файл .env и укажите TELEGRAM_BOT_TOKEN!${NC}"
    echo -e "${YELLOW}   nano $PROJECT_DIR/.env${NC}"
fi

# Применение миграций базы данных
echo -e "${YELLOW}🗄️  Применение миграций базы данных...${NC}"
if command -v alembic &> /dev/null; then
    alembic upgrade head
else
    echo -e "${YELLOW}   Alembic не найден, миграции будут применены при первом запуске${NC}"
fi

# Установка systemd service
echo -e "${YELLOW}🔧 Установка systemd service...${NC}"
sudo cp qr-code-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qr-code-bot.service

echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo -e "${YELLOW}Следующие шаги:${NC}"
echo "1. Отредактируйте файл .env: nano $PROJECT_DIR/.env"
echo "2. Запустите бота: sudo systemctl start qr-code-bot"
echo "3. Проверьте статус: sudo systemctl status qr-code-bot"
echo "4. Просмотр логов: sudo journalctl -u qr-code-bot -f"

