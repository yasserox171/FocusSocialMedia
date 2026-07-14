"""
Django settings for the Focus Social platform.

Every sensitive/environment-dependent value is read from environment
variables so the same code runs locally, in Docker, and on the future
on-premise server. See ../../.env.example for the full list.
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core -----------------------------------------------------------------

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "daphne",  # ASGI runserver
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "corsheaders",
    # local apps
    "accounts",
    "posts",
    "messaging",
    "notifications",
    "aiagents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "focus.urls"

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

WSGI_APPLICATION = "focus.wsgi.application"
ASGI_APPLICATION = "focus.asgi.application"

# --- Database ---------------------------------------------------------------
# PostgreSQL when POSTGRES_HOST is set (Docker / production),
# SQLite otherwise (quick local development without Docker).

if os.environ.get("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "focus"),
            "USER": os.environ.get("POSTGRES_USER", "focus"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "focus"),
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Channels (WebSockets) ----------------------------------------------------
# Redis channel layer in Docker/production, in-memory fallback for local dev.

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                # channels_redis defaults to a 5s socket_timeout with no
                # retry, which is too tight on a resource-constrained local
                # Docker/WSL2 host — a brief CPU/IO stall on the machine is
                # enough to kill the WebSocket listener with a raw
                # redis.exceptions.TimeoutError. Widen the timeout and let
                # it retry instead of tearing down the connection.
                "hosts": [{
                    "address": REDIS_URL,
                    "socket_timeout": int(os.environ.get("REDIS_SOCKET_TIMEOUT", 30)),
                    "socket_connect_timeout": int(os.environ.get("REDIS_SOCKET_TIMEOUT", 30)),
                    "retry_on_timeout": True,
                    "health_check_interval": 30,
                }],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

# --- Auth ---------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}

# Shared secret allowing the AI-agents worker to fetch configs and mint
# tokens for agent accounts. Must match AGENT_WORKER_SECRET on the worker.
AGENT_WORKER_SECRET = os.environ.get("AGENT_WORKER_SECRET", "")

# --- i18n ---------------------------------------------------------------------

LANGUAGE_CODE = "ar"
TIME_ZONE = os.environ.get("TIME_ZONE", "Africa/Casablanca")
USE_I18N = True
USE_TZ = True

# --- Static & media -------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", BASE_DIR / "media")

# Media storage: local filesystem by default; flip USE_S3=1 (plus the
# AWS_* variables) to move to any S3-compatible storage without touching code.
if os.environ.get("USE_S3", "0") == "1":
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL")  # MinIO etc.

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS ------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL", "1") == "1"
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# Uploaded file size limit (bytes) — 50MB default to allow short videos.
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 50 * 1024 * 1024))
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
