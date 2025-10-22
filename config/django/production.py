from .base import *


DEBUG = False
HOST = os.getenv('HOST')
ALLOWED_HOSTS = [HOST,]
CSRF_TRUSTED_ORIGINS = [
    f'https://{HOST}',
]
BASE_URL: str = f'https://{HOST}'
AGENTS_BASE_URL = os.getenv('AGENTS_BASE_URL')
AGENTS_TOKEN = os.getenv('AGENTS_TOKEN')


required_vars = ['HOST', 'AGENTS_BASE_URL', 'AGENTS_TOKEN']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

from config.settings.sentry import *

