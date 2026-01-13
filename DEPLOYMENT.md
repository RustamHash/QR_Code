# Развертывание на VPS (adminvps)

Инструкция по развертыванию QR Code Generator Bot на VPS сервере.

## Требования

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.10 или выше
- Git
- sudo права

## Быстрое развертывание

### 1. Подключитесь к серверу

```bash
ssh user@adminvps
```

### 2. Запустите скрипт развертывания

```bash
curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy.sh | bash
```

Или вручную:

```bash
git clone https://github.com/RustamHash/QR_Code.git /opt/qr_code_bot
cd /opt/qr_code_bot
chmod +x deploy.sh
./deploy.sh
```

### 3. Настройте переменные окружения

```bash
nano /opt/qr_code_bot/.env
```

Укажите:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `ADMIN_ID` - ваш Telegram ID (опционально)

### 4. Запустите бота

```bash
sudo systemctl start qr-code-bot
sudo systemctl enable qr-code-bot  # автозапуск при перезагрузке
```

### 5. Проверьте статус

```bash
sudo systemctl status qr-code-bot
```

## Управление ботом

### Просмотр логов

```bash
# Все логи
sudo journalctl -u qr-code-bot

# Последние 100 строк
sudo journalctl -u qr-code-bot -n 100

# В реальном времени
sudo journalctl -u qr-code-bot -f
```

### Управление службой

```bash
# Запуск
sudo systemctl start qr-code-bot

# Остановка
sudo systemctl stop qr-code-bot

# Перезапуск
sudo systemctl restart qr-code-bot

# Статус
sudo systemctl status qr-code-bot

# Отключить автозапуск
sudo systemctl disable qr-code-bot
```

## Развертывание через Docker

### 1. Установите Docker и Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонируйте репозиторий

```bash
git clone https://github.com/RustamHash/QR_Code.git /opt/qr_code_bot
cd /opt/qr_code_bot
```

### 3. Создайте .env файл

```bash
cp .env.example .env
nano .env
```

### 4. Запустите через Docker Compose

```bash
docker-compose build
docker-compose up -d
```

### 5. Просмотр логов

```bash
docker-compose logs -f
```

## Обновление бота

### При использовании systemd

```bash
cd /opt/qr_code_bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart qr-code-bot
```

### При использовании Docker

```bash
cd /opt/qr_code_bot
git pull origin main
docker-compose build
docker-compose up -d
```

## Резервное копирование

### База данных

```bash
# Создание бэкапа
cp /opt/qr_code_bot/bot_database.db /opt/qr_code_bot/backups/bot_database_$(date +%Y%m%d_%H%M%S).db

# Восстановление
cp /opt/qr_code_bot/backups/bot_database_YYYYMMDD_HHMMSS.db /opt/qr_code_bot/bot_database.db
```

### Автоматическое резервное копирование (cron)

Добавьте в crontab:

```bash
crontab -e
```

Добавьте строку (бэкап каждый день в 2:00):

```bash
0 2 * * * cp /opt/qr_code_bot/bot_database.db /opt/qr_code_bot/backups/bot_database_$(date +\%Y\%m\%d).db
```

## Мониторинг

### Проверка использования ресурсов

```bash
# CPU и память
top -p $(pgrep -f "python.*main.py")

# Или через systemd
systemctl status qr-code-bot
```

### Проверка дискового пространства

```bash
df -h
du -sh /opt/qr_code_bot
```

## Устранение проблем

### Бот не запускается

1. Проверьте логи:
```bash
sudo journalctl -u qr-code-bot -n 50
```

2. Проверьте .env файл:
```bash
cat /opt/qr_code_bot/.env
```

3. Проверьте права доступа:
```bash
ls -la /opt/qr_code_bot
```

### Ошибки базы данных

```bash
# Проверьте права на файл БД
ls -la /opt/qr_code_bot/bot_database.db

# Примените миграции вручную
cd /opt/qr_code_bot
source venv/bin/activate
alembic upgrade head
```

### Проблемы с зависимостями

```bash
cd /opt/qr_code_bot
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Безопасность

### Firewall (UFW)

```bash
# Установка UFW (если не установлен)
sudo apt install ufw

# Разрешить SSH
sudo ufw allow 22/tcp

# Включить firewall
sudo ufw enable
```

### Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

## Структура директорий

```
/opt/qr_code_bot/
├── src/              # Исходный код
├── alembic/          # Миграции БД
├── tests/            # Тесты
├── venv/             # Виртуальное окружение
├── bot_database.db   # База данных
├── bot.log           # Логи
├── .env              # Конфигурация
└── main.py           # Точка входа
```

## Поддержка

При возникновении проблем:
1. Проверьте логи: `sudo journalctl -u qr-code-bot -f`
2. Проверьте GitHub Issues: https://github.com/RustamHash/QR_Code/issues
3. Создайте новый Issue с описанием проблемы

