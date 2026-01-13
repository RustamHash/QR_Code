# PowerShell скрипт для получения информации о сервере через Timeweb Cloud API
# Использование: .\deploy-timeweb-api.ps1

$apiToken = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoibnM1NTIwMDEiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJkMTBkMmJlNi02MTE0LTQ3YmYtOWFmNi1lMmZjZTk2ZDdiNzgiLCJpYXQiOjE3NjgzMTkzNjh9.hLG1EvLkmPybv9bmR2J193AY9lYklOcjU8jiOkXWnnESj5NwZ7HDLef4kAGrzh7_3rmHiVX2VXK7jTYU2ox0Pydem-oNsZqwF9Gi_DXcDdarvjS9cCK5YD3Z8hdQzkMSnSYRIvBM4KoT-11tbX-Ocx1xPHfFAijd5X-njvpeuyb2tOYVJTRhBtF-hcdKKt31D5GgEeXdDaQGyKXStx44Cb4W0CSorpLGAO7hnMQv8_YM2OxWOt57d8ykc3mt7cRsMzNUFN180TifPEjpwmSsf3h8bxdV7gJSIeFcAPXa5OIkvMqSeItcb4iUuoFBYFbf4QBBTlG4Hk4_1tWtS3GYpnyRaugYLWLaKe5q4Uar6-77roho-FcpIK_kUnoPChfmaEdMGMY-kKCMn91XTdap3IlQEti0aWrZF2na5VYmrJHgq_AFbB2Imm6dzS8MDNPiLoMIJdPwsz_-TUeHmd3eaM7PQOuAn2F-LAll0kVdswsMhchd_QzEGBb6SAuure19"

$headers = @{
    "Authorization" = "Bearer $apiToken"
    "Content-Type" = "application/json"
}

Write-Host "🔍 Получение информации о сервере через Timeweb Cloud API..." -ForegroundColor Green

try {
    # Получение списка серверов
    $response = Invoke-RestMethod -Uri "https://api.timeweb.cloud/api/v1/servers" -Method Get -Headers $headers
    
    Write-Host "✅ Серверы найдены:" -ForegroundColor Green
    if ($response.servers) {
        $response.servers | ForEach-Object {
            Write-Host "  - ID: $($_.id), Имя: $($_.name), IP: $($_.ip)" -ForegroundColor Yellow
        }
        
        # Поиск сервера ns552001
        $server = $response.servers | Where-Object { $_.name -like "*ns552001*" -or $_.id -eq "6393649" }
        
        if ($server) {
            Write-Host ""
            Write-Host "📋 Информация о сервере:" -ForegroundColor Cyan
            Write-Host "   ID: $($server.id)" -ForegroundColor White
            Write-Host "   Имя: $($server.name)" -ForegroundColor White
            Write-Host "   IP: $($server.ip)" -ForegroundColor White
            Write-Host "   Статус: $($server.status)" -ForegroundColor White
            Write-Host ""
            Write-Host "Для подключения используйте:" -ForegroundColor Yellow
            Write-Host "   ssh root@$($server.ip)" -ForegroundColor White
        } else {
            Write-Host "⚠️  Сервер ns552001 не найден в списке" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Ошибка при обращении к API: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Команды для развертывания на сервере:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy-timeweb.sh | bash" -ForegroundColor White
Write-Host ""
Write-Host "Или вручную выполните команды из deploy-timeweb.sh" -ForegroundColor Yellow
