# Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Настройка конфигурации

Скопируйте `.env.example` в `.env` и заполните:

```bash
copy .env.example .env
```

Отредактируйте `.env`:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `ADMIN_ID` - ваш Telegram ID (опционально, для уведомлений)

## 3. Инициализация базы данных

База данных создастся автоматически при первом запуске.

Или вручную:
```bash
python -c "from src.database.database import init_database; init_database()"
```

## 4. Запуск бота

```bash
python main.py
```

## 5. Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Отправьте Excel файл или текстовое сообщение
4. Получите PDF с QR-кодами!

## Docker запуск

```bash
# Создайте .env файл
copy .env.example .env
# Отредактируйте .env

# Запустите
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## Получение Telegram ID

Используйте бота [@userinfobot](https://t.me/userinfobot) для получения вашего Telegram ID.

