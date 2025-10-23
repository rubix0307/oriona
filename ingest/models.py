from django.db import models
from django.utils import timezone

from common.models import TimeStampedModel
from ingest.choices import ArticleStatus


class Site(TimeStampedModel):
    slug = models.SlugField(unique=True)
    base_url = models.URLField()
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'

    def __str__(self):
        return f'{self.slug} ({self.base_url})'


class Category(TimeStampedModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.site.slug} / {self.name}'


class Article(TimeStampedModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='articles')
    url = models.URLField()
    status = models.CharField(
        max_length=32,
        choices=ArticleStatus.choices,
        default=ArticleStatus.NEW,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )

    title = models.CharField(max_length=500, blank=True)
    image_preview = models.URLField(null=True, blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    discovered_at = models.DateTimeField(default=timezone.now, editable=False)

    last_seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        unique_together = [('site', 'url')]

    def __str__(self):
        return self.url


class ArticleContent(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='content')

    content_html = models.TextField(null=True, blank=True)
    content_text = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Article Content'
        verbose_name_plural = 'Article Contents'

    def __str__(self) -> str:
        return f'content<{self.article_id}>'