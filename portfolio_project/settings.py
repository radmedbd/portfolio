from pathlib import Path
import os

import dj_database_url

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# LOAD LOCAL .env
# =========================================================

if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


# =========================================================
# CORE SECURITY
# =========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-only-change-me",
)

DEBUG = os.getenv(
    "DEBUG",
    "True",
).strip().lower() == "true"


# =========================================================
# ALLOWED HOSTS
# =========================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]

RENDER_EXTERNAL_HOSTNAME = os.getenv(
    "RENDER_EXTERNAL_HOSTNAME",
    "",
).strip()

if (
    RENDER_EXTERNAL_HOSTNAME
    and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS
):
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# =========================================================
# CSRF TRUSTED ORIGINS
# =========================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://*.onrender.com",
    ).split(",")
    if origin.strip()
]


# =========================================================
# CLOUDINARY
# =========================================================

CLOUDINARY_URL = os.getenv(
    "CLOUDINARY_URL",
    "",
).strip()

CLOUDINARY_CLOUD_NAME = os.getenv(
    "CLOUDINARY_CLOUD_NAME",
    "",
).strip()

CLOUDINARY_API_KEY = os.getenv(
    "CLOUDINARY_API_KEY",
    "",
).strip()

CLOUDINARY_API_SECRET = os.getenv(
    "CLOUDINARY_API_SECRET",
    "",
).strip()

USE_CLOUDINARY = bool(
    CLOUDINARY_URL
    or (
        CLOUDINARY_CLOUD_NAME
        and CLOUDINARY_API_KEY
        and CLOUDINARY_API_SECRET
    )
)

if USE_CLOUDINARY:
    import cloudinary

    if CLOUDINARY_URL:
        cloudinary.config(secure=True)
    else:
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True,
        )

    cloudinary_cfg = cloudinary.config()

    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": cloudinary_cfg.cloud_name,
        "API_KEY": cloudinary_cfg.api_key,
        "API_SECRET": cloudinary_cfg.api_secret,
        "SECURE": True,
    }

else:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": "",
        "API_KEY": "",
        "API_SECRET": "",
        "SECURE": True,
    }


# =========================================================
# INSTALLED APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # IMPORTANT:
    # Keep Django staticfiles BEFORE cloudinary_storage.
    # Static files are handled by WhiteNoise.
    "django.contrib.staticfiles",

    # Cloudinary is used only for uploaded media.
    "cloudinary_storage",
    "cloudinary",

    "core.apps.CoreConfig",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URLS / WSGI
# =========================================================

ROOT_URLCONF = "portfolio_project.urls"

WSGI_APPLICATION = "portfolio_project.wsgi.application"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

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


# =========================================================
# DATABASE
# =========================================================
#
# LOCAL:
#   DATABASE_URL empty/missing -> SQLite
#
# RENDER:
#   DATABASE_URL set -> PostgreSQL
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
).strip()

if DATABASE_URL:
    database_config = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
    )

    database_config["CONN_HEALTH_CHECKS"] = True

    DATABASES = {
        "default": database_config,
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator",
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
# MEDIA
# =========================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# STORAGE
# =========================================================

if USE_CLOUDINARY:
    DEFAULT_MEDIA_BACKEND = (
        "cloudinary_storage.storage."
        "MediaCloudinaryStorage"
    )
else:
    DEFAULT_MEDIA_BACKEND = (
        "django.core.files.storage."
        "FileSystemStorage"
    )

STORAGES = {
    "default": {
        "BACKEND": DEFAULT_MEDIA_BACKEND,
    },

    "staticfiles": {
        "BACKEND":
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage",
    },
}


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# GMAIL AUTOMATION
# =========================================================

PORTFOLIO_GMAIL = os.getenv(
    "PORTFOLIO_GMAIL",
    "physicist.cmch@gmail.com",
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    "",
).replace(" ", "").strip()

if EMAIL_HOST_PASSWORD:
    DEFAULT_EMAIL_BACKEND = (
        "django.core.mail.backends."
        "smtp.EmailBackend"
    )
else:
    DEFAULT_EMAIL_BACKEND = (
        "django.core.mail.backends."
        "console.EmailBackend"
    )

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    DEFAULT_EMAIL_BACKEND,
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.gmail.com",
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        "587",
    )
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    PORTFOLIO_GMAIL,
)

EMAIL_USE_TLS = os.getenv(
    "EMAIL_USE_TLS",
    "True",
).strip().lower() == "true"

EMAIL_USE_SSL = os.getenv(
    "EMAIL_USE_SSL",
    "False",
).strip().lower() == "true"

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ValueError(
        "EMAIL_USE_TLS and EMAIL_USE_SSL "
        "cannot both be True."
    )

EMAIL_TIMEOUT = int(
    os.getenv(
        "EMAIL_TIMEOUT",
        "30",
    )
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    PORTFOLIO_GMAIL,
)

CONTACT_NOTIFICATION_EMAIL = os.getenv(
    "CONTACT_NOTIFICATION_EMAIL",
    PORTFOLIO_GMAIL,
)


# =========================================================
# SCHOLARLY API SETTINGS
# =========================================================

CROSSREF_MAILTO = os.getenv(
    "CROSSREF_MAILTO",
    PORTFOLIO_GMAIL,
)

SEMANTIC_SCHOLAR_API_KEY = os.getenv(
    "SEMANTIC_SCHOLAR_API_KEY",
    "",
).strip()

OPENALEX_MAILTO = os.getenv(
    "OPENALEX_MAILTO",
    CROSSREF_MAILTO,
)


# =========================================================
# CACHE
# =========================================================

CACHES = {
    "default": {
        "BACKEND":
            "django.core.cache.backends."
            "locmem.LocMemCache",

        "LOCATION":
            "portfolio-cache",
    }
}


# =========================================================
# SECURITY
# =========================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

CSRF_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SAMESITE = "Lax"


# =========================================================
# HTTPS / PRODUCTION SECURITY
# =========================================================
#
# IMPORTANT:
# Local Django development server only supports HTTP.
#
# LOCAL .env:
#   SECURE_SSL_REDIRECT=False
#
# RENDER:
#   SECURE_SSL_REDIRECT=True
#
# Do not tie this setting directly to DEBUG.
# =========================================================

SECURE_SSL_REDIRECT = os.getenv(
    "SECURE_SSL_REDIRECT",
    "False",
).strip().lower() == "true"

if SECURE_SSL_REDIRECT:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

else:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
