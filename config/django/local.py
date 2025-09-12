from .base import *


DEBUG = True
ALLOWED_HOSTS = ['*']

HOST = os.getenv('HOST', 'localhost')
BASE_URL: str = f'https://{HOST}'

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_WORKER_POOL = 'solo'