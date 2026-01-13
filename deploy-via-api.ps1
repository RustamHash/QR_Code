# Автоматическое развертывание через Timeweb Cloud API
# Использование: .\deploy-via-api.ps1

$apiToken = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoibnM1NTIwMDEiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJkMTBkMmJlNi02MTE0LTQ3YmYtOWFmNi1lMmZjZTk2ZDdiNzgiLCJpYXQiOjE3NjgzMTkzNjh9.hLG1EvLkmPybv9bmR2J193AY9lYklOcjU8jiOkXWnnESj5NwZ7HDLef4kAGrzh7_3rmHiVX2VXK7jTYU2ox0Pydem-oNsZqwF9Gi_DXcDdarvjS9cCK5YD3Z8hdQzkMSnSYRIvBM4KoT-11tbX-Ocx1xPHfFAijd5X-njvpeuyb2tOYVJTRhBtF-hcdKKt31D5GgEeXdDaQGyKXStx44Cb4W0CSorpLGAO7hnMQv8_YM2OxWOt57d8ykc3mt7cRsMzNUFN180TifPEjpwmSsf3h8bxdV7gJSIeFcAPXa5OIkvMqSeItcb4iUuoFBYFbf4QBBTlG4Hk4_1tWtS3GYpnyRaugYLWLaKe5q4Uar6-77roho-FcpIK_kUnoPChfmaEdMGMY-kKCMn91XTdap3IlQEti0aWrZF2na5VYmrJHgq_AFbB2Imm6dzS8MDNPiLoMIJdPwsz_-TUeHmd3eaM7PQOuAn2F-LAll0kVdswsMhchd_QzEGBb6SAuure19"

$baseUrl = "https://api.timeweb.cloud/api/v1"
$headers = @{
    "Authorization" = "Bearer $apiToken"
    "Content-Type" = "application/json"
}

Write-Host "🚀 Автоматическое развертывание через Timeweb Cloud API..." -ForegroundColor Green

try {
    Write-Host "📡 Получение информации о серверах..." -ForegroundColor Yellow
    $serversResponse = Invoke-RestMethod -Uri "$baseUrl/servers" -Method Get -Headers $headers
    
    $server = $null
    if ($serversResponse.servers) {
        $server = $serversResponse.servers | Where-Object { 
            $_.name -like "*ns552001*" -or $_.id -eq 6393649 -or $_.id -eq "6393649" 
        } | Select-Object -First 1
    }
    
    if (-not $server) {
        Write-Host "❌ Сервер не найден. Доступные серверы:" -ForegroundColor Red
        if ($serversResponse.servers) {
            $serversResponse.servers | ForEach-Object {
                Write-Host "  - ID: $($_.id), Имя: $($_.name)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "✅ Сервер найден:" -ForegroundColor Green
        Write-Host "   ID: $($server.id)" -ForegroundColor White
        Write-Host "   Имя: $($server.name)" -ForegroundColor White
        Write-Host "   IP: $($server.ip)" -ForegroundColor White
        Write-Host "   Статус: $($server.status)" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Ошибка при обращении к API: $_" -ForegroundColor Red
    Write-Host "   Это нормально, если API не поддерживает эту операцию" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Инструкции для развертывания:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Используйте веб-консоль Timeweb Cloud:" -ForegroundColor Yellow
Write-Host "1. Войдите в панель: https://timeweb.cloud/" -ForegroundColor White
Write-Host "2. Откройте веб-консоль для сервера ns552001" -ForegroundColor White
Write-Host "3. Выполните команду ниже" -ForegroundColor White
Write-Host ""
Write-Host "Команда для выполнения на сервере:" -ForegroundColor Yellow
Write-Host "curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy-timeweb.sh | bash" -ForegroundColor Green
Write-Host ""
