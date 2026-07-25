# Deployment / CI-CD Runbook

CI/CD for **mysite** runs on GitHub Actions ([.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)):

- **CI** (every push + PR to `main`): install deps → `manage.py check` → check for missing
  migrations → `manage.py test`.
- **CD** (push to `main`, only if CI passes): SSH into the VPS → `git pull` →
  `pip install` → `migrate` → `collectstatic` → restart gunicorn.

You do the two one-time setups below once. After that, **every `git push` to `main`
auto-deploys**.

---

## 1. One-time: GitHub repository secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add:

| Secret name    | Value                                                              |
| -------------- | ----------------------------------------------------------------- |
| `VPS_HOST`     | `134.209.66.211`                                                  |
| `VPS_USER`     | `root`                                                            |
| `VPS_SSH_KEY`  | The **entire** private key file `deploy_key` (see below), incl. the `-----BEGIN/END-----` lines |

The deploy keypair was generated for you in your scratchpad:

- Private key: `…/scratchpad/deploy_key`  → paste its full contents into `VPS_SSH_KEY`
- Public key (also below) → goes on the server in step 2

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHm4Y7ESKjhRBTIYTEhklfYj5oRawMq2VsRYCHromfgi github-actions-deploy-mysite
```

---

## 2. One-time: prepare the VPS

SSH into the server as root and run:

```bash
# a) Authorize the GitHub Actions deploy key
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHm4Y7ESKjhRBTIYTEhklfYj5oRawMq2VsRYCHromfgi github-actions-deploy-mysite' >> ~/.ssh/authorized_keys

# b) Turn /var/www/mysite into a clone of the GitHub repo.
#    (venv/ and db.sqlite3 are git-ignored, so they are preserved.)
cd /var/www/mysite
git init
git remote add origin https://github.com/jimjerry00b/mysite.git
git fetch origin
git checkout -f -b main origin/main

# c) Create the production .env (never committed). Use a REAL secret key:
cat > /var/www/mysite/.env <<EOF
DJANGO_SECRET_KEY=$(venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=134.209.66.211,localhost,127.0.0.1
EOF
chmod 600 /var/www/mysite/.env

# d) Install the new deps + updated systemd unit (adds EnvironmentFile)
venv/bin/pip install -r requirements.txt
cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
systemctl daemon-reload

# e) First deploy by hand to confirm everything works
bash scripts/deploy.sh
```

Then browse to <http://134.209.66.211/mysite/admin/> to confirm the site (and admin
CSS, now served by WhiteNoise) works.

---

## 3. Push the clean code (from your PC)

> The repo already contains an earlier "first commit" (with `db.sqlite3` and the old
> hardcoded key). The clean history here replaces it, so a **force-push** is required:

```bash
cd c:\vps\mysite
git push -u origin main --force
```

That push kicks off CI. Every push after that runs CI and, on `main`, deploys
automatically. Watch runs under the repo's **Actions** tab.

### Security remediation (because the old data was public)

- **Rotate the Django admin password** after the first deploy (the old DB was public):
  `venv/bin/python manage.py changepassword <username>`
- The old `SECRET_KEY` is replaced by the new one in `/var/www/.env` (step 2c), so it is
  already rotated for the running app.
- The old commit `87e28f9` may remain reachable by its SHA on GitHub until their GC runs.
  For a fully clean slate, **delete and recreate** the GitHub repo, then push `main`.

---

## Notes / what changed

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` now come from environment variables
  (`config/settings.py`), fed by `/var/www/mysite/.env` via the systemd `EnvironmentFile`.
  **Required** because this repo is public — no secrets in git.
- **WhiteNoise** was added so static files (admin CSS) work under gunicorn with
  `DEBUG=False`. The deploy runs `collectstatic` into `staticfiles/` (git-ignored).
- `db.sqlite3` and `venv/` are git-ignored; the server keeps its own copies.
- To deploy manually at any time, SSH in and run `bash scripts/deploy.sh`.

## Database (MySQL — shared by local and live)

The app uses **MySQL** on the VPS. Both the live site and local dev talk to the
**same** database, so the config is env-driven ([config/settings.py](config/settings.py)):

- `DJANGO_DB_ENGINE=mysql` switches from the SQLite fallback to MySQL.
- Connection comes from `DJANGO_DB_NAME/USER/PASSWORD/HOST/PORT`.
- Driver is **PyMySQL** (pure-Python; installs with no compiler on Windows/Linux).

**Live** (`/var/www/mysite/.env`): connects on the VPS loopback —
`DJANGO_DB_HOST=127.0.0.1`, `DJANGO_DB_PORT=3306`.

**Local**: MySQL stays private on the VPS (bound to `127.0.0.1`, never exposed).
Reach it through an SSH tunnel:

```powershell
# Terminal 1 — open the tunnel (local 3307 -> VPS 127.0.0.1:3306). Keep it open.
powershell -ExecutionPolicy Bypass -File scripts\db-tunnel.ps1

# Terminal 2 — run the app (reads .env: DJANGO_DB_HOST=127.0.0.1, PORT=3307)
venv\Scripts\python manage.py runserver
```

> ⚠️ It's the **same** database — migrations or edits you make locally change
> **live production data** immediately. There is no separate dev copy.

The pre-MySQL `db.sqlite3` is kept on the server as a backup. To roll back,
remove the `DJANGO_DB_*` lines from `.env` and restart gunicorn.

## Local development

```powershell
cd c:\vps\mysite
python -m venv venv
venv\Scripts\pip install -r requirements.txt
# Create a local .env (git-ignored): DJANGO_DEBUG=True + the DJANGO_DB_* vars
# pointing at 127.0.0.1:3307 (see "Database" above).
powershell -ExecutionPolicy Bypass -File scripts\db-tunnel.ps1   # keep open
venv\Scripts\python manage.py runserver                          # in another terminal
```
