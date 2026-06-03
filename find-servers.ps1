# find-servers.ps1
# Запуск: .ind-servers.ps1  (из открытого терминала)

# Фиксим кодировку — без этого кириллица показывается кракозябрами
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

Write-Host "`n=== Слушающие порты ===" -ForegroundColor Cyan
netstat -ano | Select-String "LISTENING" | ForEach-Object {
    $parts = ($_ -replace "\s+", " ").Trim() -split " "
    $addr  = $parts[1]
    $port  = ($addr -split ":")[-1]
    $pid_  = $parts[4]
    if ($port -gt 1000 -and $pid_ -match "^\d+$") {
        $proc = Get-Process -Id $pid_ -ErrorAction SilentlyContinue
        if ($proc) {
            [PSCustomObject]@{
                Port    = [int]$port
                Process = $proc.Name
                PID     = $pid_
            }
        }
    }
} | Sort-Object Port | Format-Table -AutoSize

Write-Host "`n=== Python / Node процессы ===" -ForegroundColor Yellow
Get-Process -Name "python*","node*","uvicorn*" -ErrorAction SilentlyContinue |
    Select-Object Name, Id, @{N="RAM(MB)";E={[math]::Round($_.WorkingSet64/1MB,1)}} |
    Format-Table -AutoSize

Write-Host "`n=== Статус серверов проекта ===" -ForegroundColor Green
@(
    [PSCustomObject]@{Port=8000;  Service="ScamSence API";     URL="http://127.0.0.1:8000/docs"},
    [PSCustomObject]@{Port=8642;  Service="Hermes Gateway";    URL="http://127.0.0.1:8642"},
    [PSCustomObject]@{Port=9119;  Service="Hermes Web UI";     URL="http://127.0.0.1:9119"},
    [PSCustomObject]@{Port=3000;  Service="OpenWhispr";        URL="http://127.0.0.1:3000"},
    [PSCustomObject]@{Port=11434; Service="Ollama (LLM!)";     URL="http://127.0.0.1:11434"},
    [PSCustomObject]@{Port=1234;  Service="LM Studio (LLM!)";  URL="http://127.0.0.1:1234"},
    [PSCustomObject]@{Port=6333;  Service="Qdrant (vectors)";  URL="http://127.0.0.1:6333"}
) | ForEach-Object {
    $busy   = Get-NetTCPConnection -LocalPort $_.Port -State Listen -ErrorAction SilentlyContinue
    $status = if ($busy) { "RUNNING" } else { "stopped" }
    $color  = if ($busy) { "Green"   } else { "DarkGray" }
    Write-Host ("  [{0,-8}] {1,-22} {2}" -f $status, $_.Service, $_.URL) -ForegroundColor $color
}
Write-Host ""
Read-Host "Press Enter to close"
