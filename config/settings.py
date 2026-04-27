from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-in-production-2026")
DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes", "on"}

ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "accounts",
    "enrollments",
    "team",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

db_engine = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
if db_engine == "django.db.backends.sqlite3":
    database_name = os.getenv("DB_NAME", str(BASE_DIR / "db.sqlite3"))
else:
    database_name = os.getenv("DB_NAME", "")

DATABASES = {
    "default": {
        "ENGINE": db_engine,
        "NAME": database_name,
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEAM_ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
TEAM_MAX_IMAGE_SIZE_BYTES = int(os.getenv("TEAM_MAX_IMAGE_SIZE_BYTES", str(2 * 1024 * 1024)))

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_ANON_RATE", "60/minute"),
        "user": os.getenv("THROTTLE_USER_RATE", "120/minute"),
        "login": os.getenv("THROTTLE_LOGIN_RATE", "8/minute"),
        "auth_burst": os.getenv("THROTTLE_AUTH_BURST_RATE", "20/minute"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080,https://thingkers.pabnabazar.live,https://thingkers.com,https://www.thingkers.com",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
APPEND_SLASH = False

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-only-admin-token-change-in-production-2026")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "thingkers-auth-cache",
    }
}

AUTH_MAX_FAILED_ATTEMPTS = int(os.getenv("AUTH_MAX_FAILED_ATTEMPTS", "5"))
AUTH_FAILURE_WINDOW_SECONDS = int(os.getenv("AUTH_FAILURE_WINDOW_SECONDS", "600"))
AUTH_LOCKOUT_SECONDS = int(os.getenv("AUTH_LOCKOUT_SECONDS", "900"))

AUTH_REFRESH_COOKIE_NAME = os.getenv("AUTH_REFRESH_COOKIE_NAME", "refresh_token")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "False").lower() in {"1", "true", "yes", "on"}
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "Lax")
AUTH_REFRESH_COOKIE_PATH = os.getenv("AUTH_REFRESH_COOKIE_PATH", "/api/auth/")
AUTH_REFRESH_COOKIE_MAX_AGE = int(os.getenv("AUTH_REFRESH_COOKIE_MAX_AGE", str(60 * 60 * 24 * 7)))
AUTH_SESSION_REFRESH_COOKIE_MAX_AGE = int(os.getenv("AUTH_SESSION_REFRESH_COOKIE_MAX_AGE", str(60 * 60 * 12)))
AUTH_FRONTEND_RESET_PASSWORD_URL = os.getenv("AUTH_FRONTEND_RESET_PASSWORD_URL", "http://localhost:8080/reset-password")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@thingkers.local")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = AUTH_COOKIE_SECURE
CSRF_COOKIE_SECURE = AUTH_COOKIE_SECURE
CSRF_TRUSTED_ORIGINS = [origin for origin in CORS_ALLOWED_ORIGINS if origin.startswith("http")]
