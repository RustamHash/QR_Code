# Развертывание на Timeweb Cloud

## Быстрое развертывание через веб-консоль

### Шаг 1: Откройте веб-консоль

1. Войдите в панель: https://timeweb.cloud/
2. Перейдите к вашему серверу (ns552001 / ID: 6393649)
3. Найдите кнопку "Консоль", "Web SSH" или "VNC"
4. Откройте веб-консоль в браузере

### Шаг 2: Выполните развертывание

В веб-консоли выполните одну команду:

```bash
curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy-timeweb.sh | bash
```

## Ручное развертывание

Если автоматический скрипт не работает:

```bash
# 1. Обновление системы
apt update && apt upgrade -y

# 2. Установка пакетов
apt install -y python3 python3-pip python3-venv git curl wget unzip

# 3. Скачивание проекта через зеркало
cd /opt
curl -L https://ghproxy.com/https://github.com/RustamHash/QR_Code/archive/refs/heads/main.zip -o qr_code.zip

# Если curl не работает
wget https://ghproxy.com/https://github.com/RustamHash/QR_Code/archive/refs/heads/main.zip -O qr_code.zip

# 4. Распаковка
unzip qr_code.zip
mv QR_Code-main qr_code_bot
cd qr_code_bot

# 5. Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# 7. Создание .env
cp .env.example .env
nano .env  # Укажите TELEGRAM_BOT_TOKEN
```

В файле `.env` укажите:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `ADMIN_ID` - ваш Telegram ID (опционально)

```bash
# 8. Применение миграций
alembic upgrade head

# 9. Установка systemd service
cp qr-code-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qr-code-bot
systemctl start qr-code-bot

# 10. Проверка статуса
systemctl status qr-code-bot

# 11. Просмотр логов
journalctl -u qr-code-bot -f
```

## Использование API токена

Если у вас есть API токен Timeweb Cloud, вы можете использовать его для получения информации о сервере:

```powershell
# На локальном компьютере
.\deploy-via-api.ps1
```

Этот скрипт:
- Получит информацию о сервере через API
- Покажет инструкции для развертывания
- Создаст готовый скрипт для выполнения на сервере

## Управление ботом

```bash
# Статус
systemctl status qr-code-bot

# Перезапуск
systemctl restart qr-code-bot

# Остановка
systemctl stop qr-code-bot

# Логи
journalctl -u qr-code-bot -f
```

## Обновление

```bash
cd /opt/qr_code_bot
curl -L https://ghproxy.com/https://github.com/RustamHash/QR_Code/archive/refs/heads/main.zip -o qr_code.zip
unzip -o qr_code.zip
mv QR_Code-main/* .
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
systemctl restart qr-code-bot
```

## Особенности Timeweb Cloud

- **Веб-консоль**: Используйте веб-консоль для доступа к серверу
- **IPv6**: Сервер имеет IPv6 адрес: `2a03:6f00:a::1:897d`
- **API доступ**: Используйте API токен для управления через API
- **Зеркало GitHub**: Используйте `ghproxy.com` для обхода блокировки GitHub

## Поддержка

При возникновении проблем:
1. Проверьте логи: `journalctl -u qr-code-bot -f`
2. Проверьте .env файл: `cat /opt/qr_code_bot/.env`
3. Обратитесь в поддержку Timeweb Cloud

