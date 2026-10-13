from django.core.exceptions import ImproperlyConfigured

from .base import *

if env.bool("DEBUG", default=False):
    raise ImproperlyConfigured("DEBUG tidak boleh aktif pada production.")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Production membutuhkan secret acak minimal 50 karakter.")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS production harus berupa allowlist konkret.")
DATABASES = {"default": env.db()}
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("Baseline production memakai PostgreSQL; review untuk engine lain.")
DATABASES["default"]["CONN_MAX_AGE"] = 60
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=3600)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
if env.bool("TRUST_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": env("EMAIL_HOST", default="localhost"),
            "port": env.int("EMAIL_PORT", default=25),
            "username": env("EMAIL_USERNAME", default=""),
            "password": env("EMAIL_PASSWORD", default=""),
            "use_tls": env.bool("EMAIL_USE_TLS", default=False),
            "timeout": 10,
        },
    }
}
