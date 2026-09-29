from pathlib import Path
import os

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# CORE / SECURITY
# =========================================================

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"


# =========================================================
# HOSTS
# =========================================================

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if h.strip()
]

# Render automatically provides this variable.
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# =========================================================
# CSRF
# =========================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.onrender.com"
    ).split(",")
    if origin.strip()
]


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # Must be before staticfiles when using
    # django-cloudinary-storage.
    "cloudinary_storage",

    "django.contrib.staticfiles",

    "cloudinary",

    "core.apps.CoreConfig",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Static files
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "portfolio_project.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_context",
            ],
        },
    },
]


WSGI_APPLICATION = "portfolio_project.wsgi.application"


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation."
        "MinimumLengthValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation."
        "CommonPasswordValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation."
        "NumericPasswordValidator"
    },
]


# =========================================================
# LANGUAGE / TIMEZONE
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Dhaka"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================================================
# CLOUDINARY
# =========================================================
#
# Recommended:
#
# Render Environment:
#
# CLOUDINARY_CLOUD_NAME
# CLOUDINARY_API_KEY
# CLOUDINARY_API_SECRET
#
# OR CLOUDINARY_URL
#
# Cloudinary Python SDK can read CLOUDINARY_URL automatically.
# =========================================================

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET", ""),
}


# =========================================================
# FILE STORAGE
# =========================================================
#
# Uploaded IMAGES -> Cloudinary
# Static CSS/JS -> WhiteNoise
# =========================================================

STORAGES = {
    "default": {
        "BACKEND":
        "cloudinary_storage.storage.MediaCloudinaryStorage",
    },

    "staticfiles": {
        "BACKEND":
        "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Django still expects MEDIA_URL.
MEDIA_URL = "/media/"

# Only useful during local development/fallback.
MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# EMAIL
# =========================================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
)

EMAIL_USE_TLS = (
    os.getenv(
        "EMAIL_USE_TLS",
        "True",
    ).lower()
    == "true"
)

EMAIL_USE_SSL = (
    os.getenv(
        "EMAIL_USE_SSL",
        "False",
    ).lower()
    == "true"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "portfolio@example.com",
)


# =========================================================
# CROSSREF
# =========================================================

CROSSREF_MAILTO = os.getenv(
    "CROSSREF_MAILTO",
    DEFAULT_FROM_EMAIL,
)


# =========================================================
# SEMANTIC SCHOLAR
# =========================================================

SEMANTIC_SCHOLAR_API_KEY = os.getenv(
    "SEMANTIC_SCHOLAR_API_KEY",
    "",
)


# =========================================================
# CACHE
# =========================================================

CACHES = {
    "default": {
        "BACKEND":
        "django.core.cache.backends.locmem.LocMemCache",

        "LOCATION":
        "portfolio-cache",
    }
}


# =========================================================
# RENDER / HTTPS SECURITY
# =========================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SAMESITE = "Lax"


# Only enforce secure cookies in production.
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True