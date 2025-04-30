from .base import *  # noqa
from config.env import env

DEBUG = False

# Configure the domain name using the environment variable
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS") + [
    "127.0.0.1"
]  # localhost required for docker health checks

CSRF_TRUSTED_ORIGINS = [f"https://{host}/" for host in ALLOWED_HOSTS]
