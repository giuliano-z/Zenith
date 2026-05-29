"""Entorno de producción (Railway). DEBUG forzado a False; seguridad endurecida."""
from .base import *  # noqa: F401,F403

DEBUG = False

# RS-003: redirección a HTTPS y cabeceras de seguridad en producción.
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

MIDDLEWARE.insert(  # noqa: F405
    1, "whitenoise.middleware.WhiteNoiseMiddleware"
)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
