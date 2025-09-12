from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.local')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.autodiscover_tasks(['ingest.parsers.factroom'])


QUEUES = {
    'INGEST_FACTROOM': {'name': 'ingest.factroom'},
    'EMBEDDING_NEW_ARTICLES': {'name': 'ingest.semantic'},
}
QUEUE_DEFAULT_ARGS = {
    'x-max-length': 1,
    'x-overflow': 'drop-head',
    'x-message-ttl': 60*60*1000,
}
app.conf.task_queues = (
    Queue(QUEUES['INGEST_FACTROOM']['name'], queue_arguments=QUEUE_DEFAULT_ARGS),
    Queue(QUEUES['EMBEDDING_NEW_ARTICLES']['name'], queue_arguments=QUEUE_DEFAULT_ARGS),
)

app.conf.beat_schedule = {
    'parse_factroom_task_every_6h': {
        'task': 'parse_factroom_task',
        'schedule': timedelta(hours=6),
        'options': {'queue': QUEUES['INGEST_FACTROOM']['name']},
    },
    'embedding_articles': {
        'task': 'embedding_new_articles_task',
        'schedule': timedelta(hours=1),
        'options': {'queue': QUEUES['EMBEDDING_NEW_ARTICLES']['name']},
        'kwargs': {'limit': 1000},
    },
}
