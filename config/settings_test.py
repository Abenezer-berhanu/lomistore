"""Settings for pytest: no .env values leak in, no network, no Redis, no Postgres."""

import os

os.environ["DJANGO_DEBUG"] = "0"
os.environ["DJANGO_SECRET_KEY"] = "test-only-secret"

from config.settings import *  # noqa: E402, F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]  # noqa: F405  (no collected static files in tests)
ALLOWED_HOSTS = ["testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # fast, tests only

PUBLIC_BASE_URL = "https://bot.example.com"
TELEGRAM_BOT_TOKEN = "123:test"
TELEGRAM_BOT_USERNAME = "lomistore_bot"
TELEGRAM_WEBHOOK_SECRET = "test-secret"
TELEGRAM_CHANNEL_USERNAME = "lomistore"
TELEGRAM_ADMIN_CHAT_ID = -1001234567890
