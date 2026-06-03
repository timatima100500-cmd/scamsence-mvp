# install-process-compose.ps1 — скачивает и устанавливает process-compose
# Запуск: .\install-process-compose.ps1

$installDir = "$env:LOCALAPPDATA\Programs\process-compose"
$exePath    = "$installDir\process-compose.exe"
$zipPath    = "$env:TEMP\process-compose.zip"
$downloadUrl = "https://github.com/F1bonacc1/process-compose/releases/latest/download/process-compose_Windows_x86_64.zip"

Write-Host "Скачиваем process-compose..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
Expand-Archive -Path $zipPath -DestinationPath $installDir -Force
Remove-Item $zipPath

# Добавляем в PATH (для текущего пользователя, постоянно)
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$installDir", "User")
    Write-Host "Добавлен в PATH: $installDir" -ForegroundColor Green
}

# Проверяем
& $exePath --version
Write-Host ""
Write-Host "Готово! Перезапусти терминал, затем:" -ForegroundColor Green
Write-Host "  cd C:\Users\Acer\Documents\Claude\Projects\ScamSence_MVP" -ForegroundColor White
Write-Host "  process-compose up" -ForegroundColor White
Read-Host "Press Enter to close"
