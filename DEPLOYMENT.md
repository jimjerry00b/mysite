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

## Local development

```bash
cd c:\vps\mysite
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # then edit: set DJANGO_DEBUG=True
python manage.py migrate
python manage.py runserver
```
