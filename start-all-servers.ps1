# start-all-servers.ps1 — запускает весь стек с задержками
# Запуск: .\start-all-servers.ps1  (из pwsh / PowerShell 7)

$ScamRoot   = "C:\Users\Acer\Documents\Claude\Projects\ScamSence_MVP"
$HermesScript = "C:\Users\Acer\hermes-workspace\Start-Hermes-V2.ps1"
$WhisprDir  = "C:\Users\Acer\Desktop\openwhispr"

if (-not (Get-Command wt -ErrorAction SilentlyContinue)) {
    Write-Host "Windows Terminal (wt) не найден." -ForegroundColor Red
    Read-Host "Press Enter"; exit
}

Write-Host "Запускаем стек..." -ForegroundColor Cyan

# 1. OpenWhispr (Electron/Node — самый долгий старт, запускаем первым)
wt --title "OpenWhispr" pwsh -NoExit -Command "
  Write-Host '=== OpenWhispr (voice dictation) ===' -ForegroundColor Green
  cd '$WhisprDir'
  npm run dev
"

Start-Sleep -Seconds 4

# 2. Hermes stack (gateway + dashboard + vite) — использует оригинальный скрипт
wt -w 0 new-tab --title "Hermes Stack" pwsh -NoExit -Command "
  Write-Host '=== Hermes Stack ===' -ForegroundColor Yellow
  Write-Host '  Gateway  → http://127.0.0.1:8642'
  Write-Host '  Web UI   → http://127.0.0.1:9119'
  Write-Host '  Vite     → http://localhost:3000'
  & '$HermesScript'
"

Start-Sleep -Seconds 6

# 3. ScamSence API
wt -w 0 new-tab --title "ScamSence API" pwsh -NoExit -Command "
  Write-Host '=== ScamSence API → http://127.0.0.1:8000/docs ===' -ForegroundColor Cyan
  cd '$ScamRoot'
  .venv\Scripts\Activate
  uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
"

Start-Sleep -Seconds 3

# 4. Shell — для тестов
wt -w 0 new-tab --title "Shell" pwsh -NoExit -Command "
  cd '$ScamRoot'
  .venv\Scripts\Activate
  Write-Host '=== Shell (тесты + команды) ===' -ForegroundColor White
  Write-Host '  .\find-servers.ps1  — статус всех серверов' -ForegroundColor DarkGray
  Write-Host '  `$b = @{content=`"test`";content_type=`"text`"} | ConvertTo-Json' -ForegroundColor DarkGray
  Write-Host '  Invoke-RestMethod http://127.0.0.1:8000/api/v1/analyze -Method POST -ContentType application/json -Body `$b' -ForegroundColor DarkGray
"

Write-Host "Готово! Все вкладки открыты в Windows Terminal." -ForegroundColor Green
Write-Host "Порядок старта: OpenWhispr → Hermes → ScamSence → Shell" -ForegroundColor DarkGray
Start-Sleep -Seconds 2
