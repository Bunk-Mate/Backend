import os

from .settings import *

# Configure the domain name using the environment variable
ALLOWED_HOSTS = (
    os.environ["WEBSITE_HOSTNAMES"].split(",") + ["127.0.0.1"]
    if "WEBSITE_HOSTNAMES" in os.environ
    else ["127.0.0.1"]
)
CSRF_TRUSTED_ORIGINS = (
    [f"https://{domain}" for domain in os.environ["WEBSITE_HOSTNAMES"].split(",")]
    if "WEBSITE_HOSTNAMES" in os.environ
    else []
)
DEBUG = False
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Configure Postgres database based on connection string of the libpq Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DBENGINE"),
        "NAME": os.environ.get("DBNAME"),
        "HOST": os.environ.get("DBHOST"),
        "USER": os.environ.get("DBUSER"),
        "PASSWORD": os.environ.get("DBPASS"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("CACHELOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "app"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s] " "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}
