import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SEGURIDAD DE VARIABLES DE ENTORNO =================
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "0") == "1"

NGROK_DOMAIN = (
    os.environ.get("NGROK_DOMAIN", "")
    .replace("https://", "")
    .replace("http://", "")
    .strip("/")
    .strip()
)

ALLOWED_HOSTS = list(set(
    [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",") if h.strip()]
    + [
        ".ngrok-free.app",
        ".ngrok-free.dev",
        ".trycloudflare.com",
        ".onrender.com",
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
    ]
    + ([NGROK_DOMAIN] if NGROK_DOMAIN else [])
))

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "https://*.trycloudflare.com",
    "https://*.onrender.com",
]
if NGROK_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{NGROK_DOMAIN}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto (Vertical Slices)
    "apps.shared",
    "apps.catalog",
    "apps.calculator",
    "apps.palette_lab",
    "apps.sales",
    "apps.contractors",
]

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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.sales.context_processors.carrito_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DB_OPTIONS = {"connect_timeout": 10}
if os.environ.get("POSTGRES_SSLMODE"):
    DB_OPTIONS["sslmode"] = os.environ["POSTGRES_SSLMODE"]

# ================= CONEXIÓN SEGURA A POSTGRESQL (PUERTO 5435) =================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "tienda_epoxica_db"),
        "USER": os.environ.get("POSTGRES_USER", "admin_db"),
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5435"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ================= CABECERAS DE SEGURIDAD HTTP / COOKIES =================
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
