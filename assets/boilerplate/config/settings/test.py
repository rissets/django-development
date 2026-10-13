import os

os.environ.setdefault("DJANGO_SECRET_KEY", "isolated-test-key-not-for-deployment")
from .base import *  # noqa: E402

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = {"default": env.db_url("TEST_DATABASE_URL", default="sqlite:///:memory:")}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
LOGGING["root"]["level"] = "ERROR"
LOGGING["loggers"] = {
    "django.request": {"level": "CRITICAL"},
    "django.security.csrf": {"level": "CRITICAL"},
}
# Asset serving gets a separate production/static smoke test.
MIDDLEWARE = [m for m in MIDDLEWARE if m != "whitenoise.middleware.WhiteNoiseMiddleware"]
