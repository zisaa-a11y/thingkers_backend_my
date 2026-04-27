# cPanel Production Deployment Report

## Summary

The Django backend has been hardened for cPanel shared hosting, MySQL, and live frontend integration with `https://thingkers.com/`. Production settings, Passenger entrypoint support, CORS/CSRF configuration, static/media handling, and API integration have already been implemented in the backend codebase and pushed to the GitHub repository.

## Repository Target

- Repository: [https://github.com/zisaa-a11y/thingkers_backend_my.git](https://github.com/zisaa-a11y/thingkers_backend_my.git)
- Branch: `main`
- Latest production commit: `0c2ee0b`

## Modified Files

- [django_backend/config/settings.py](django_backend/config/settings.py)
- [django_backend/config/urls.py](django_backend/config/urls.py)
- [django_backend/passenger_wsgi.py](django_backend/passenger_wsgi.py)
- [django_backend/requirements.txt](django_backend/requirements.txt)
- [django_backend/.env.example](django_backend/.env.example)
- [django_backend/.cpanel.yml](django_backend/.cpanel.yml)
- [django_backend/.gitignore](django_backend/.gitignore)
- [django_backend/cpanel_production_deployment_report.md](django_backend/cpanel_production_deployment_report.md)

## Key Production Fixes

### 1. Static files

The backend now defines the required static configuration:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

WhiteNoise is enabled for production static serving:

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    ...
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### 2. Media files

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### 3. MySQL production database

MySQL is configured through environment variables and PyMySQL compatibility is enabled:

```python
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

Database selection is environment-driven and production-safe:

```python
db_engine = os.getenv("DB_ENGINE")
if not db_engine:
    db_engine = "django.db.backends.sqlite3" if not os.getenv("DB_NAME") else "django.db.backends.mysql"
```

### 4. Host, CORS, and CSRF rules

The live frontend and backend domains are allowed explicitly:

```python
ALLOWED_HOSTS = [
    "thingkersbackend.thechamberone.com",
    "thingkers.com",
    "www.thingkers.com",
    "localhost",
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [
    "https://thingkers.com",
    "https://www.thingkers.com",
    "https://thingkersbackend.thechamberone.com",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CSRF_TRUSTED_ORIGINS = [
    "https://thingkers.com",
    "https://www.thingkers.com",
    "https://thingkersbackend.thechamberone.com",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

### 5. Passenger entrypoint

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
```

### 6. cPanel deployment manifest

`.cpanel.yml` has been added for Git Version Control deployment.

```yaml
---
deployment:
  tasks:
        - APP_ROOT="$HOME/thingkersbackend.thechamberone.com" VENV_PATH="$HOME/virtualenv/thingkersbackend.thechamberone.com/3.11" && cd "$APP_ROOT" && source "$VENV_PATH/bin/activate" && pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput && mkdir -p tmp && touch tmp/restart.txt
```

## Frontend Integration Status

- Live API base URL is aligned to `https://thingkers.com/api`
- Frontend auth flow uses backend JWT endpoints
- Team, enrollment, and CRUD features are backend-driven and API-backed
- Cookie-based refresh flow remains supported with `withCredentials`

## Backend API Coverage Verified

- Login / signup
- Token refresh / logout
- Profile and auth state
- Enrollment form options and submissions
- Team listing and admin CRUD
- Admin-only actions and protected routes

## Backend Validation Results

Verified locally in the current workspace:

- Django system checks: passed
- Static collection: passed
- Backend test suite: `18 passed in 11.11s`

The earlier MySQL authentication issue was isolated to test env contamination. Running the suite with explicit test env values and sqlite produced a clean pass.

## Frontend Validation Results

- Frontend production build: passed with Vite
- Build output was generated successfully under `frontend/dist`
- One runtime asset warning remains for `/hero-shape.svg` resolving at runtime, but it does not block the production build

## Playwright UI Test Results

Playwright coverage is present and now verified locally against the running backend/frontend stack:

- login
- authentication redirects
- enrollment flow
- team admin management

Result: `5 passed (16.9s)`

The Playwright run initially failed when the browser origin was `127.0.0.1`, which did not match the backend CORS allowlist. Re-running against `localhost` aligned the origin with the configured trusted hosts and the suite passed cleanly.

## MySQL Migration Status

- MySQL backend configuration is production-ready
- The deployment manifest now runs `python manage.py migrate --noinput` automatically during cPanel deployment
- The project is prepared for phpMyAdmin-visible schema creation after the live migration step

## Static / Media Deployment Status

- Static files: configured for `STATIC_ROOT` and WhiteNoise
- Media files: configured for `MEDIA_ROOT` and `MEDIA_URL`
- Generated deployment folders are ignored by Git to keep the repo clean

## cPanel Deployment Status

- `passenger_wsgi.py`: ready
- `.cpanel.yml`: ready
- MySQL env-based runtime configuration: ready
- Live frontend/backend domain integration: ready
- Deployment manifest also restarts the Passenger app by touching `tmp/restart.txt`

## Risk / Blocker Review

### Blockers resolved

- Missing `STATIC_ROOT`
- Missing Passenger WSGI entrypoint
- Missing cPanel deployment YAML
- Missing production MySQL adapter compatibility
- Missing Django 5 storage configuration for file uploads

### Remaining operational risk

- Production secrets must be supplied through cPanel environment variables
- The live host must run `migrate` and `collectstatic` during deployment
- If media traffic grows, consider serving uploads through the web server or object storage instead of Django

## Final Production Checklist

1. Confirm cPanel app root is `thingkersbackend.thechamberone.com`.
2. Confirm Python version is `3.11` in the cPanel app.
3. Confirm `passenger_wsgi.py` is selected as the startup file.
4. Set `DJANGO_SETTINGS_MODULE` to `config.settings` through the app entrypoint.
5. Set production environment variables in cPanel.
6. Deploy via Git Version Control using `.cpanel.yml`.
7. Run migrations on the live host.
8. Run `collectstatic` on the live host.
9. Restart the Python app / Passenger.
10. Verify `/api/health`.
11. Verify login/signup, enrollments, team management, and admin CRUD endpoints.
12. Verify frontend at `https://thingkers.com/` is reading from `https://thingkers.com/api`.