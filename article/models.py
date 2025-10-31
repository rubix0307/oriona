import datetime

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from agent.schemas.common import Language
from article.choices import IdeaStatus
from common.models import TimeStampedModel


class ArticleIdea(TimeStampedModel):

    title = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)
    source_ingest = models.ForeignKey(
        'ingest.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ideas',
    )
    status = models.CharField(
        max_length=20,
        choices=IdeaStatus.choices,
        default=IdeaStatus.CREATED,
    )
    language = models.CharField(max_length=2, choices=Language.choices(), default=Language.RU.value)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(source_ingest__isnull=False)
                    | (Q(title__isnull=False) & ~Q(title=''))
                ),
                name='articleidea_title_or_ingest_required',
            ),
        ]

    def clean(self):
        if not self.source_ingest and not self.title:
            raise ValidationError('Title or source_ingest is required')

    def save(self, *args, **kwargs):
        if self.source_ingest and not self.title:
            self.title = getattr(self.source_ingest, 'title', '') or self.title
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

class ArticleProcess(TimeStampedModel):
    idea = models.ForeignKey(ArticleIdea, on_delete=models.CASCADE, related_name='processes')
    agent_name = models.CharField(max_length=100)
    result = models.JSONField(blank=True)


def article_image_upload_path(instance, filename):
    now = datetime.date.today()
    return f"articles/images/{now.year}/{now.month:02d}/{filename}"

class Article(TimeStampedModel):
    idea = models.ForeignKey(ArticleIdea, on_delete=models.CASCADE)

    image = models.ImageField(
        upload_to=article_image_upload_path,
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=120)
    content = models.TextField()


