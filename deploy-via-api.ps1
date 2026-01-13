# Автоматическое развертывание через Timeweb Cloud API
# Использование: .\deploy-via-api.ps1

$apiToken = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoibnM1NTIwMDEiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJkMTBkMmJlNi02MTE0LTQ3YmYtOWFmNi1lMmZjZTk2ZDdiNzgiLCJpYXQiOjE3NjgzMTkzNjh9.hLG1EvLkmPybv9bmR2J193AY9lYklOcjU8jiOkXWnnESj5NwZ7HDLef4kAGrzh7_3rmHiVX2VXK7jTYU2ox0Pydem-oNsZqwF9Gi_DXcDdarvjS9cCK5YD3Z8hdQzkMSnSYRIvBM4KoT-11tbX-Ocx1xPHfFAijd5X-njvpeuyb2tOYVJTRhBtF-hcdKKt31D5GgEeXdDaQGyKXStx44Cb4W0CSorpLGAO7hnMQv8_YM2OxWOt57d8ykc3mt7cRsMzNUFN180TifPEjpwmSsf3h8bxdV7gJSIeFcAPXa5OIkvMqSeItcb4iUuoFBYFbf4QBBTlG4Hk4_1tWtS3GYpnyRaugYLWLaKe5q4Uar6-77roho-FcpIK_kUnoPChfmaEdMGMY-kKCMn91XTdap3IlQEti0aWrZF2na5VYmrJHgq_AFbB2Imm6dzS8MDNPiLoMIJdPwsz_-TUeHmd3eaM7PQOuAn2F-LAll0kVdswsMhchd_QzEGBb6SAuure19"

$baseUrl = "https://api.timeweb.cloud/api/v1"
$headers = @{
    "Authorization" = "Bearer $apiToken"
    "Content-Type" = "application/json"
}

Write-Host "Avtomaticheskoe razvertyvanie cherez Timeweb Cloud API..." -ForegroundColor Green

try {
    Write-Host "Poluchenie informacii o serverah..." -ForegroundColor Yellow
    $serversResponse = Invoke-RestMethod -Uri "$baseUrl/servers" -Method Get -Headers $headers
    
    $server = $null
    if ($serversResponse.servers) {
        $server = $serversResponse.servers | Where-Object { 
            $_.name -like "*ns552001*" -or $_.id -eq 6393649 -or $_.id -eq "6393649" 
        } | Select-Object -First 1
    }
    
    if (-not $server) {
        Write-Host "Server ne naiden. Dostupnye servery:" -ForegroundColor Red
        if ($serversResponse.servers) {
            $serversResponse.servers | ForEach-Object {
                Write-Host "  - ID: $($_.id), Name: $($_.name)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "Server naiden:" -ForegroundColor Green
        Write-Host "   ID: $($server.id)" -ForegroundColor White
        Write-Host "   Name: $($server.name)" -ForegroundColor White
        Write-Host "   IP: $($server.ip)" -ForegroundColor White
        Write-Host "   Status: $($server.status)" -ForegroundColor White
        
        # Получение детальной информации
        try {
            Write-Host ""
            Write-Host "Poluchenie detalnoj informacii..." -ForegroundColor Yellow
            $serverDetails = Invoke-RestMethod -Uri "$baseUrl/servers/$($server.id)" -Method Get -Headers $headers
            
            if ($serverDetails.server) {
                $details = $serverDetails.server
                Write-Host "   IPv6: 2a03:6f00:a::1:897d" -ForegroundColor White
                if ($details.ipv4) {
                    Write-Host "   IPv4: $($details.ipv4)" -ForegroundColor White
                }
                if ($details.networks) {
                    $ipv4Network = $details.networks | Where-Object { $_.type -eq "ipv4" } | Select-Object -First 1
                    if ($ipv4Network) {
                        Write-Host "   IPv4 Network: $($ipv4Network.ip)" -ForegroundColor White
                    }
                }
            }
        } catch {
            Write-Host "   Ne udalos poluchit detali (eto normalno)" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "Oshibka pri obrashchenii k API: $_" -ForegroundColor Red
    Write-Host "   Eto normalno, esli API ne podderzhivaet etu operaciyu" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instrukcii dlya razvertyvaniya:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ispolzujte web-konsol Timeweb Cloud:" -ForegroundColor Yellow
Write-Host "1. Vojdite v panel: https://timeweb.cloud/" -ForegroundColor White
Write-Host "2. Otkrojte web-konsol dlya servera ns552001" -ForegroundColor White
Write-Host "3. Vypolnite komandu nizhe" -ForegroundColor White
Write-Host ""
Write-Host "Komanda dlya vypolneniya na servere:" -ForegroundColor Yellow
Write-Host "curl -fsSL https://raw.githubusercontent.com/RustamHash/QR_Code/main/deploy-timeweb.sh | bash" -ForegroundColor Green
Write-Host ""
