from .base import *


DEBUG = False
HOST = os.getenv('HOST')
ALLOWED_HOSTS = [HOST,]
CSRF_TRUSTED_ORIGINS = [
    f'https://{HOST}',
]
BASE_URL: str = f'https://{HOST}'
if not HOST:
    raise ValueError('Please set the HOST environment variable')
AGENTS_BASE_URL = os.getenv('AGENTS_BASE_URL')
AGENTS_TOKEN = os.getenv('AGENTS_TOKEN')

from config.settings.sentry import *

