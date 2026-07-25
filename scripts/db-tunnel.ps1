# Opens an SSH tunnel so LOCAL Django can reach the shared MySQL database on the
# VPS without exposing MySQL to the internet. Keep this window open while you
# develop locally; run the app in a separate terminal.
#
#   Local 127.0.0.1:3307  --(encrypted SSH)-->  VPS 127.0.0.1:3306 (MySQL)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\db-tunnel.ps1
# Then, in another terminal:
#   venv\Scripts\python manage.py runserver

Write-Host "Opening SSH tunnel to VPS MySQL (local 3307 -> VPS 127.0.0.1:3306)." -ForegroundColor Cyan
Write-Host "Keep this window open. Press Ctrl+C to close the tunnel." -ForegroundColor Cyan
ssh -N -L 3307:127.0.0.1:3306 root@134.209.66.211
