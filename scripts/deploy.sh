#!/usr/bin/env bash
# Manual deploy for mysite. Run ON THE SERVER from /var/www/mysite:
#   bash scripts/deploy.sh
# (The GitHub Actions pipeline runs the same steps automatically.)
set -euo pipefail

cd "$(dirname "$0")/.."   # repo root

echo "==> Pulling latest code"
git pull --ff-only origin main

echo "==> Installing dependencies"
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# Load environment (SECRET_KEY, DEBUG, ALLOWED_HOSTS) for management commands
set -a; [ -f .env ] && . ./.env; set +a

echo "==> Applying migrations"
venv/bin/python manage.py migrate --noinput

echo "==> Collecting static files"
venv/bin/python manage.py collectstatic --noinput

echo "==> Restarting gunicorn"
systemctl restart gunicorn
systemctl is-active gunicorn

echo "==> Deploy complete"
