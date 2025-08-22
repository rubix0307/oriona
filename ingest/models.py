# crawling/models.py
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )

    title = models.CharField(max_length=500, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=[
            ('NEW', 'NEW'),
            ('FETCHED', 'FETCHED'),
            ('PARSED', 'PARSED'),
            ('ERROR', 'ERROR'),
        ],
        default='NEW',
    )
    error_note = models.TextField(blank=True)

    discovered_at = models.DateTimeField(default=timezone.now, editable=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_crawled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        unique_together = [('site', 'url')]
        indexes = [
            models.Index(fields=['site', 'status']),
            models.Index(fields=['site', 'last_crawled_at']),
        ]

    def __str__(self):
        return self.url