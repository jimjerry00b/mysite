# One command to run the site locally.
#
# Opens the MySQL SSH tunnel, waits until it is ready, then starts the Django
# dev server. Press Ctrl+C to stop the server -- the tunnel is closed for you.
#
# Usage (from anywhere):
#   powershell -ExecutionPolicy Bypass -File c:\vps\mysite\scripts\run-local.ps1
# or, from c:\vps\mysite:
#   .\scripts\run-local.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Test-Port($portNumber) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect('127.0.0.1', $portNumber)
        $client.Close()
        return $true
    } catch { return $false }
}

# If the tunnel is already up (e.g. another window), don't start a second one.
$ownsTunnel = $false
$tunnel = $null
if (Test-Port 3307) {
    Write-Host "Tunnel already running on port 3307 - reusing it." -ForegroundColor Yellow
} else {
    Write-Host "Opening MySQL SSH tunnel (127.0.0.1:3307 -> VPS 127.0.0.1:3306)..." -ForegroundColor Cyan
    $tunnel = Start-Process ssh -PassThru -WindowStyle Hidden -ArgumentList @(
        '-N', '-o', 'BatchMode=yes', '-o', 'ServerAliveInterval=30',
        '-o', 'ExitOnForwardFailure=yes',
        '-L', '3307:127.0.0.1:3306', 'root@134.209.66.211'
    )
    $ownsTunnel = $true
}

try {
    # Wait for the tunnel to accept connections (avoids the startup race).
    for ($i = 0; $i -lt 40; $i++) {
        if (Test-Port 3307) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not (Test-Port 3307)) { throw "Tunnel did not come up on port 3307 (check SSH)." }

    Write-Host "Tunnel ready. Starting server at http://127.0.0.1:8000/ (Ctrl+C to stop)`n" -ForegroundColor Green
    & "$root\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
}
finally {
    if ($ownsTunnel -and $tunnel -and -not $tunnel.HasExited) {
        Write-Host "`nClosing SSH tunnel..." -ForegroundColor Yellow
        Stop-Process -Id $tunnel.Id -Force
    }
}
