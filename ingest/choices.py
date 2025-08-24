from django.db.models import TextChoices


class ArticleStatus(TextChoices):
    NEW = 'NEW', 'NEW'
    FETCHED = 'FETCHED', 'FETCHED'
    PARSED = 'PARSED', 'PARSED'
    ERROR = 'ERROR', 'ERROR'