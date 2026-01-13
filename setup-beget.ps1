# PowerShell скрипт для развертывания на Beget через SSH
# Использование: .\setup-beget.ps1

$ErrorActionPreference = "Stop"

$serverIP = "31.128.36.34"
$username = "root"
$password = "mgo&7!%TmmUa"

Write-Host "🚀 Развертывание QR Code Bot на Beget Cloud..." -ForegroundColor Green

# Проверка доступности
Write-Host "📡 Проверка доступности сервера..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $serverIP -Count 2 -Quiet
if (-not $ping) {
    Write-Host "❌ Сервер недоступен!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Сервер доступен" -ForegroundColor Green

# Создание временного файла с командами
$commands = @"
#!/bin/bash
set -e
echo '🚀 Начало развертывания...'

# Обновление системы
apt update && apt upgrade -y

# Установка пакетов
apt install -y python3 python3-pip python3-venv git

# Создание директории
mkdir -p /opt/qr_code_bot
cd /opt/qr_code_bot

# Клонирование репозитория
if [ -d .git ]; then
    git pull origin main
else
    git clone https://github.com/RustamHash/QR_Code.git .
fi

# Виртуальное окружение
if [ ! -d venv ]; then
    python3 -m venv venv
fi

# Установка зависимостей
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env (если не существует)
if [ ! -f .env ]; then
    cp .env.example .env
    echo '⚠️  Отредактируйте .env файл: nano /opt/qr_code_bot/.env'
fi

# Применение миграций
alembic upgrade head

# Установка systemd service
cp qr-code-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qr-code-bot

echo '✅ Развертывание завершено!'
echo '⚠️  Не забудьте отредактировать .env файл перед запуском!'
"@

$commands | Out-File -FilePath "deploy-temp.sh" -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Инструкции для подключения:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Подключитесь к серверу:" -ForegroundColor Yellow
Write-Host "   ssh $username@$serverIP" -ForegroundColor White
Write-Host ""
Write-Host "2. Пароль: $password" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. После подключения выполните:" -ForegroundColor Yellow
Write-Host "   curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy-beget-auto.sh | bash" -ForegroundColor White
Write-Host ""
Write-Host "Или скопируйте и выполните команды из deploy-beget-auto.sh" -ForegroundColor Gray

